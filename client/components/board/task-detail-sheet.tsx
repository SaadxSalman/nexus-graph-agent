import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

export const TaskDetailSheet = ({ task, isOpen, onClose }: any) => (
  <Sheet open={isOpen} onOpenChange={onClose}>
    <SheetContent className="w-[400px] sm:w-[540px]">
      <SheetHeader>
        <SheetTitle>{task.title}</SheetTitle>
      </SheetHeader>
      <div className="space-y-6 mt-4">
        {/* Editor, File Uploads, and Deadlines go here */}
      </div>
    </SheetContent>
  </Sheet>
);