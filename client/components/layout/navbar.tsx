// client/components/layout/navbar.tsx
import { UserNav } from "./user-nav";
import { MobileSidebar } from "./mobile-sidebar";

export const Navbar = () => {
  return (
    <nav className="fixed top-0 w-full h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-50 px-4">
      <div className="flex h-full items-center justify-between">
        <div className="flex items-center gap-x-4">
          <MobileSidebar /> {/* Hidden on desktop */}
          <span className="font-bold text-xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Nexus
          </span>
        </div>
        <div className="flex items-center gap-x-2">
          <UserNav />
        </div>
      </div>
    </nav>
  );
};