// client/components/board/task-card.tsx
import { Draggable } from "@hello-pangea/dnd";

export const TaskCard = ({ task, index }: { task: any; index: number }) => (
  <Draggable draggableId={task._id} index={index}>
    {(provided) => (
      <div
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        ref={provided.innerRef}
        className="bg-card p-3 mb-2 rounded-lg border shadow-sm hover:border-blue-500 transition-colors"
      >
        <p className="text-sm font-medium">{task.title}</p>
        {task.dueDate && <span className="text-xs text-muted-foreground">{task.dueDate}</span>}
      </div>
    )}
  </Draggable>
);