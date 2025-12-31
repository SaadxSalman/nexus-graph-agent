import { Schema, model } from 'mongoose';

const CommentSchema = new Schema({
  content: { type: String, required: true },
  author: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  taskId: { type: Schema.Types.ObjectId, ref: 'Task' }, 
  workspaceId: { type: Schema.Types.ObjectId, ref: 'Workspace' }
}, { timestamps: true });

export const Comment = model('Comment', CommentSchema);