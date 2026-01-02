// client/components/layout/sidebar.tsx
"use client";
import { motion } from "framer-motion";
import { useState } from "react";

export const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <motion.aside
      animate={{ width: isCollapsed ? 80 : 240 }}
      className="hidden md:flex flex-col h-full border-r bg-card transition-all"
    >
      <div className="p-4 flex-1 flex flex-col gap-y-2">
        {/* Nav Links here */}
      </div>
    </motion.aside>
  );
};