import { createContext, useContext, type ReactNode } from "react";

type NotificationContextValue = {
  register: () => Promise<string | null>;
};

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function NotificationProvider({
  children,
  register,
}: {
  children: ReactNode;
  register: () => Promise<string | null>;
}) {
  return <NotificationContext.Provider value={{ register }}>{children}</NotificationContext.Provider>;
}

export function useNotificationRegistration() {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error("useNotificationRegistration must be used inside NotificationProvider.");
  }
  return ctx;
}
