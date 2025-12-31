import { Schema, model } from 'mongoose';

const TaskSchema = new Schema({
  title: { type: String, required: true },
  description: { type: String },
  status: { type: String, default: 'todo' },
  priority: { type: String, enum: ['low', 'medium', 'high', 'urgent'], default: 'medium' },
  assignees: [{ type: Schema.Types.ObjectId, ref: 'User' }],
  boardId: { type: Schema.Types.ObjectId, ref: 'Board', required: true },
  order: { type: Number, default: 0 }
}, { timestamps: true });

const BoardSchema = new Schema({
  title: { type: String, required: true },
  workspaceId: { type: Schema.Types.ObjectId, ref: 'Workspace', required: true },
  lists: [{
    name: { type: String, required: true },
    taskOrder: [{ type: Schema.Types.ObjectId, ref: 'Task' }]
  }]
}, { timestamps: true });

export const Task = model('Task', TaskSchema);
export const Board = model('Board', BoardSchema);