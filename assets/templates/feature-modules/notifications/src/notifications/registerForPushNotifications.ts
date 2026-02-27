import * as Notifications from "expo-notifications";

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
