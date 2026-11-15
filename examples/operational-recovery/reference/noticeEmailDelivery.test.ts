import assert from "node:assert/strict";
import test from "node:test";
import {
  isNoticeEmailDeliveryEnabled,
  parseNoticeEmailQueueMessage,
  serializeNoticeEmailQueueMessage,
} from "./noticeEmailDelivery.ts";

const deliveryId =
  "00000000-0000-4000-8000-000000000005";

test(
  "Notice email queue payload is exactly version plus deliveryId",
  () => {
    const serialized =
      serializeNoticeEmailQueueMessage(
        deliveryId
      );

    assert.deepEqual(
      JSON.parse(serialized),
      {
        version: 1,
        deliveryId,
      }
    );

    assert.deepEqual(
      parseNoticeEmailQueueMessage(
        serialized
      ),
      {
        version: 1,
        deliveryId,
      }
    );

    assert.throws(
      () =>
        parseNoticeEmailQueueMessage({
          version: 1,
          deliveryId,
          recipientEmail:
            "not-allowed@example.com",
        })
    );
  }
);

test(
  "Notice email GUID parsing accepts canonical GUID shape without UUID-version restriction",
  () => {
    assert.equal(
      parseNoticeEmailQueueMessage({
        version: 1,
        deliveryId:
          "00000000-0000-4000-8000-000000000006",
      }).deliveryId,
      "00000000-0000-4000-8000-000000000006"
    );
  }
);

test(
  "Notice email delivery is disabled unless explicitly true",
  () => {
    assert.equal(
      isNoticeEmailDeliveryEnabled(
        {}
      ),
      false
    );

    assert.equal(
      isNoticeEmailDeliveryEnabled({
        NOTICE_EMAIL_DELIVERY_ENABLED:
          "false",
      }),
      false
    );

    assert.equal(
      isNoticeEmailDeliveryEnabled({
        NOTICE_EMAIL_DELIVERY_ENABLED:
          "true",
      }),
      true
    );
  }
);
