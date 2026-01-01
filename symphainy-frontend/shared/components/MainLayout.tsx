"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import dynamic from "next/dynamic";
import ChatPanelUI from "./chatbot/ChatPanelUI";
import SecondaryChatPanelUI from "./chatbot/SecondaryChatPanelUI";

const InteractiveChat = dynamic(() => import("./chatbot/InteractiveChat"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
});

const InteractiveSecondaryChat = dynamic(() => import("./chatbot/InteractiveSecondaryChat"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
});
import { FileText, BarChart2, Settings, FlaskConical } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TopNavBar from "./TopNavBar";
import ChatbotToggleDemo from "@/components/examples/ChatbotToggleDemo";
import { 
  mainChatbotOpenAtom,
  shouldShowSecondaryChatbotAtom,
  primaryChatbotTransformAtom,
  secondaryChatbotPositionAtom,
  primaryChatbotHeightAtom
} from "../atoms";
import { useAtomValue } from "jotai";
import { useChatbotRouteReset } from "@/shared/hooks/useChatbotRouteReset";
import { useAuth } from "@/shared/agui/AuthProvider";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  // ✅ ONE line - automatically resets chatbot on route changes
  useChatbotRouteReset();
  
  // ✅ Check authentication status - only render chat panel when authenticated
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { guideSessionToken } = useGlobalSession();
  
  // Get current route to highlight the active tab
  const pathname = usePathname();
  
  // ✅ CRITICAL: Exclude ONLY authentication routes from chat panel rendering
  // Landing page (/) SHOULD have chat capabilities for guide agent showcase
  // Only exclude routes where authentication is not yet complete
  const authRoutes = ['/login', '/register'];
  const isAuthRoute = authRoutes.includes(pathname);
  
  // ✅ CRITICAL: Verify that guideSessionToken matches auth_token
  // This prevents rendering chat with an invalid or mismatched token
  const authToken = typeof window !== 'undefined' ? localStorage.getItem("auth_token") : null;
  const tokenMatches = authToken && guideSessionToken && authToken === guideSessionToken;
  
  // ✅ STRICT AUTH CHECK: Only render chat when:
  // 1. NOT on authentication routes (/login, /register) - landing page (/) is allowed
  // 2. Auth is not loading
  // 3. User is authenticated
  // 4. Valid session token exists (not empty, not placeholder)
  // 5. Token is a valid string (not just truthy)
  // 6. Token matches auth token (prevents using wrong token)
  // 7. Add small delay to ensure auth state is fully settled (prevents race conditions)
  const [authReady, setAuthReady] = useState(false);
  
  useEffect(() => {
    // Small delay to ensure auth state is fully settled before allowing chat to render
    // This prevents race conditions where components mount before token is ready
    if (!authLoading && isAuthenticated && guideSessionToken && tokenMatches) {
      const timer = setTimeout(() => {
        setAuthReady(true);
      }, 100); // 100ms delay to ensure state is settled
      return () => clearTimeout(timer);
    } else {
      setAuthReady(false);
    }
  }, [authLoading, isAuthenticated, guideSessionToken, tokenMatches]);
  
  const shouldRenderChat = 
    !isAuthRoute && // ✅ CRITICAL: Never render on auth routes, but allow landing page
    !authLoading && 
    isAuthenticated && 
    guideSessionToken && 
    typeof guideSessionToken === 'string' &&
    guideSessionToken.trim() !== '' && 
    guideSessionToken !== 'token_placeholder' &&
    guideSessionToken.length > 10 && // Ensure token is substantial (not just a few chars)
    tokenMatches && // ✅ CRITICAL: Token must match auth token
    authReady; // ✅ CRITICAL: Wait for auth state to settle
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  
  // Get derived atoms for animations
  const showSecondary = useAtomValue(shouldShowSecondaryChatbotAtom);
  const primaryTransform = useAtomValue(primaryChatbotTransformAtom);
  const secondaryPosition = useAtomValue(secondaryChatbotPositionAtom);
  const primaryHeight = useAtomValue(primaryChatbotHeightAtom);

  return (
    <div className="flex min-h-screen min-w-screen overflow-hidden bg-white">
      <TopNavBar />
      <div className="flex-1 flex flex-col min-w-0">
        {/* Main Content */}
        <div className="flex flex-row bg-gray-100 overflow-y-auto gap-6 p-4 md:p-8 mt-20">
          <div className="w-[72%] bg-gray-100">{children}</div>
          <div className="w-[23%] bg-gray-100"></div>
        </div>
      </div>
      {/* Chatbot Container with Animations - Only render when fully authenticated with valid token */}
      {shouldRenderChat && (
        <div className="fixed bottom-0 right-0 z-50">

          {/* Secondary Chatbot - Slides in from right when main is closed */}
          <div 
            className={`
              absolute bottom-0 right-0
              transition-all duration-300 ease-in-out
              ${secondaryPosition}
              ${showSecondary ? 'z-50' : 'z-30 pointer-events-none opacity-0'}
            `}
            style={{
              transform: `${secondaryPosition}`,
            }}
          >
            <div className="h-[87vh] w-[24vw] min-w-[330px] max-w-[400px]">
              <SecondaryChatPanelUI>
                <InteractiveSecondaryChat />
              </SecondaryChatPanelUI>
            </div>
          </div>

          {/* Primary Chatbot - Always present, slides down when secondary shows */}
          <div 
            className={`
              bottom-0 right-0
              transition-all duration-300 ease-in-out
              ${primaryTransform}
              ${mainChatbotOpen ? 'z-50' : 'z-40 pointer-events-none opacity-40'}
            `}
            style={{
              transform: `${primaryTransform}`,
            }}
          >
            <div className={`${primaryHeight} w-[24vw] min-w-[330px] max-w-[400px]`}>
              <ChatPanelUI>
                <InteractiveChat />
              </ChatPanelUI>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
