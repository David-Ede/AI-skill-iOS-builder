import { getLocales } from "expo-localization";
import { messages } from "./messages/en";

export function getLocaleCode() {
  const locale = getLocales()[0];
  return locale?.languageCode ?? "en";
}

export function t(key: keyof typeof messages): string {
  return messages[key];
}
