import type { ReactNode } from "react";
import { FluentProvider as BaseFluentProvider, webLightTheme } from "@fluentui/react-components";

interface FluentProviderProps {
  children: ReactNode;
}

export function FluentProvider({ children }: FluentProviderProps) {
  return <BaseFluentProvider theme={webLightTheme}>{children}</BaseFluentProvider>;
}
