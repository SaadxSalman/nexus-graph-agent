// client/components/ui/user-avatar.tsx
import Image from "next/image";
import { cn } from "@/lib/utils";

interface UserAvatarProps {
  src?: string | null;
  name?: string;
  className?: string;
}

export const UserAvatar = ({ src, name, className }: UserAvatarProps) => {
  return (
    <div className={cn("relative h-8 w-8 rounded-full overflow-hidden bg-secondary", className)}>
      {src ? (
        <Image 
          src={src} 
          alt={name || "User avatar"} 
          fill 
          className="object-cover" 
          sizes="32px"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-xs font-medium uppercase">
          {name?.charAt(0) || "U"}
        </div>
      )}
    </div>
  );
};