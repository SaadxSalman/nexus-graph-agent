import { Schema, model } from 'mongoose';

const WorkspaceSchema = new Schema({
  name: { type: String, required: true },
  description: { type: String },
  owner: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  members: [{
    user: { type: Schema.Types.ObjectId, ref: 'User' },
    role: { type: String, enum: ['owner', 'member', 'viewer'], default: 'member' }
  }]
}, { timestamps: true });

export const Workspace = model('Workspace', WorkspaceSchema);