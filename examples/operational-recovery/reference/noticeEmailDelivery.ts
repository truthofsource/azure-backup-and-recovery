export type NoticeEmailQueueMessage = {
  version: 1;
  deliveryId: string;
};

const guidShape =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isNoticeEmailDeliveryEnabled(
  environment:
    NodeJS.ProcessEnv = process.env
): boolean {
  return (
    environment
      .NOTICE_EMAIL_DELIVERY_ENABLED
      ?.trim()
      .toLowerCase() === "true"
  );
}

export function normalizeNoticeEmailGuid(
  value: unknown,
  fieldName: string
): string {
  if (
    typeof value !== "string" ||
    !guidShape.test(value.trim())
  ) {
    throw new Error(
      `${fieldName} must be a GUID.`
    );
  }

  return value.trim().toLowerCase();
}

export function parseNoticeEmailQueueMessage(
  value: unknown
): NoticeEmailQueueMessage {
  let parsed: unknown = value;

  if (typeof value === "string") {
    try {
      parsed = JSON.parse(value);
    } catch {
      throw new Error(
        "Notice email queue message must be valid JSON."
      );
    }
  }

  if (
    typeof parsed !== "object" ||
    parsed === null ||
    Array.isArray(parsed)
  ) {
    throw new Error(
      "Notice email queue message must be an object."
    );
  }

  const record =
    parsed as Record<string, unknown>;

  const keys =
    Object.keys(record).sort();

  if (
    keys.length !== 2 ||
    keys[0] !== "deliveryId" ||
    keys[1] !== "version" ||
    record.version !== 1
  ) {
    throw new Error(
      "Notice email queue message has an invalid shape."
    );
  }

  return {
    version: 1,
    deliveryId:
      normalizeNoticeEmailGuid(
        record.deliveryId,
        "deliveryId"
      ),
  };
}

export function serializeNoticeEmailQueueMessage(
  deliveryId: string
): string {
  return JSON.stringify({
    version: 1,
    deliveryId:
      normalizeNoticeEmailGuid(
        deliveryId,
        "deliveryId"
      ),
  } satisfies NoticeEmailQueueMessage);
}
