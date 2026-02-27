import * as Device from "expo-device";
import * as Notifications from "expo-notifications";

export type PushRegistrationPayload = {
  expoPushToken: string;
  platform: "ios";
  deviceName?: string;
};

export async function registerForPushNotificationsAsync(): Promise<string | null> {
  const permission = await Notifications.getPermissionsAsync();
  let finalStatus = permission.status;

  if (finalStatus !== "granted") {
    const request = await Notifications.requestPermissionsAsync();
    finalStatus = request.status;
  }

  if (finalStatus !== "granted") {
    return null;
  }

  const tokenResult = await Notifications.getExpoPushTokenAsync();
  return tokenResult.data;
}

export function createPushRegistrationPayload(token: string): PushRegistrationPayload {
  return {
    expoPushToken: token,
    platform: "ios",
    deviceName: Device.deviceName ?? undefined,
  };
}

export async function registerPushTokenWithBackend(
  payload: PushRegistrationPayload,
  endpointUrl: string,
  authToken?: string,
): Promise<boolean> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };
  if (authToken) {
    headers.authorization = `Bearer ${authToken}`;
  }

  try {
    const response = await fetch(endpointUrl, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    return response.ok;
  } catch {
    return false;
  }
}
