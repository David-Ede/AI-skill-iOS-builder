import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import * as Linking from "expo-linking";
import * as Notifications from "expo-notifications";
import { extractNotificationDeepLink } from "./notificationDeepLink";

type NotificationContextValue = {
  register: () => Promise<string | null>;
  lastDeepLink: string | null;
  clearLastDeepLink: () => void;
};

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function NotificationProvider({
  children,
  register,
  onDeepLink,
}: {
  children: ReactNode;
  register: () => Promise<string | null>;
  onDeepLink?: (deepLink: string) => void;
}) {
  const [lastDeepLink, setLastDeepLink] = useState<string | null>(null);

  useEffect(() => {
    const subscription = Notifications.addNotificationResponseReceivedListener((response) => {
      const rawData = response.notification.request.content.data;
      const deepLink = extractNotificationDeepLink(rawData as Record<string, unknown>);
      if (!deepLink) {
        return;
      }

      setLastDeepLink(deepLink);
      if (onDeepLink) {
        onDeepLink(deepLink);
        return;
      }

      const destination = deepLink.includes("://") ? deepLink : Linking.createURL(deepLink);
      void Linking.openURL(destination);
    });

    return () => {
      subscription.remove();
    };
  }, [onDeepLink]);

  const value = useMemo<NotificationContextValue>(
    () => ({
      register,
      lastDeepLink,
      clearLastDeepLink: () => setLastDeepLink(null),
    }),
    [register, lastDeepLink],
  );

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotificationRegistration() {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error("useNotificationRegistration must be used inside NotificationProvider.");
  }
  return ctx;
}
