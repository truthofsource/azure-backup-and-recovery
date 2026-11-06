"""Exercise actual backup orchestration with fictional in-memory adapters."""
import contextlib,io,hashlib,json
from reference import payroll_key_recovery as key
from reference.fixtures import FakeHttp,FakeLease,TARGET
from .database_rehearsal import backup,restore,inventory

def demo():
    checks=[]
    def add(name,passed,detail):checks.append({'name':name,'passed':bool(passed),'detail':detail})
    with contextlib.redirect_stdout(io.StringIO()):
        http=FakeHttp()
        first=key.backup(http,lease_factory=FakeLease)
        add('Backup bytes match the retained checksum',hashlib.sha256(http.blobs[first['blobName']]).hexdigest()==first['sha256'],'Actual receipt/readback logic; fictional encrypted backup bytes')
        before=sum('/backup?' in url for _,url in http.calls)
        key.backup(http,lease_factory=FakeLease)
        after=sum('/backup?' in url for _,url in http.calls)
        add('Current version coverage avoids another backup',before==after,'Six-hour coverage does not mean full backup every six hours')
        http.source_versions['b'*32]={'enabled':True}
        second=key.backup(http,lease_factory=FakeLease)
        add('Changed version coverage creates a new receipt',second['blobName']!=first['blobName'] and len(second['versions'])==2,'Exact versions are part of coverage')
        result=key.restore(http,TARGET,second['receiptName'])
        add('Disposable-target version coverage is verified',result['restoreVerified'] and len(result['testedVersions'])==2,'Fake wrap/unwrap proves orchestration, not real cryptography or Azure access')
        try:key.restore(http,TARGET,second['receiptName']);blocked=False
        except key.RecoveryError:blocked=True
        add('An existing restored key cannot be overwritten',blocked,'Uncertain outcomes require reconciliation')
        fresh=FakeHttp();receipt=key.backup(fresh,lease_factory=FakeLease)
        fresh.blobs[receipt['blobName']]=b'changed'
        try:key.restore(fresh,TARGET,receipt['receiptName']);blocked=False
        except key.RecoveryError:blocked=True
        add('Changed backup bytes are rejected',blocked,'Checksum mismatch stops restore')
        race=FakeHttp();race.changed=True
        try:key.backup(race,lease_factory=FakeLease);blocked=False
        except key.RecoveryError:blocked=True
        add('Rotation during backup cannot publish success',blocked and 'latest.json' not in race.blobs,'No accepted latest pointer after a version race')
    return {'checks':checks,'metrics':[{'label':'Source tests','value':'11','detail':'Original recovery tests, fake transport'},{'label':'Versions verified','value':'2','detail':'Fictional retained versions'},{'label':'Cloud calls','value':'0','detail':'No Azure HTTP adapter included'},{'label':'Recovery layers','value':'4','detail':'Keys / database / files / state'}],
            'records':[['Key backup','Verified',first['sha256'][:16]],['Version coverage','Verified','2 fictional versions'],['Repeated restore','Rejected','Existing target preserved'],['Rotation race','Rejected','No accepted latest pointer']]}
