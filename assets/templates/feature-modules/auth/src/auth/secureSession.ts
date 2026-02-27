import * as SecureStore from "expo-secure-store";

const SESSION_KEY = "expo_ios_app_builder.session_token";

export async function saveSessionToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(SESSION_KEY, token);
}

export async function loadSessionToken(): Promise<string | null> {
  return SecureStore.getItemAsync(SESSION_KEY);
}

export async function clearSessionToken(): Promise<void> {
  await SecureStore.deleteItemAsync(SESSION_KEY);
}
