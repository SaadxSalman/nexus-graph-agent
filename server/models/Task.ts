import mongoose, { Schema, Document } from 'mongoose';

export interface ITask extends Document {
  title: string;
  status: 'TODO' | 'IN_PROGRESS' | 'DONE';
  boardId: mongoose.Types.ObjectId;
  assignee: mongoose.Types.ObjectId;
  deletedAt?: Date | null;
}

const TaskSchema = new Schema<ITask>({
  title: { type: String, required: true },
  status: {
    type: String,
    enum: ['TODO', 'IN_PROGRESS', 'DONE'],
    default: 'TODO',
  },
  boardId: { type: Schema.Types.ObjectId, ref: 'Board', required: true },
  assignee: { type: Schema.Types.ObjectId, ref: 'User' },
  deletedAt: { type: Date, default: null },
}, { timestamps: true });

export const Task = mongoose.model<ITask>('Task', TaskSchema);