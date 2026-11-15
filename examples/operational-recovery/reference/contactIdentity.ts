import {createHash} from "node:crypto";
type AttendanceChannel = "email" | "sms";
class ControlError extends Error {}
function normalizePhone(_: unknown): never {throw Error("SMS adapter is not part of this email-only reference");}
export function contactAddress(channel:AttendanceChannel,value:unknown):string {
 if(typeof value!=="string")throw new ControlError("invalid_attendance_contact");
 const address=channel==="sms"?normalizePhone(value):value.trim();
 if(channel==="sms"?!/^\+[1-9]\d{7,14}$/.test(address):address.length>254||! /^[A-Za-z0-9.!#$%&'*+\/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$/.test(address))throw new ControlError("invalid_attendance_contact");
 return channel==="email"?address.toLowerCase():address;
}
export function contactHash(channel:AttendanceChannel,address:string){return createHash("sha256").update(JSON.stringify([channel,contactAddress(channel,address)])).digest("hex");}
