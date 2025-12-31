import mongoose, { Schema, Document } from 'mongoose';

export interface IBoard extends Document {
  title: string;
  workspaceId: mongoose.Types.ObjectId;
}

const BoardSchema = new Schema<IBoard>({
  title: { type: String, required: true },
  workspaceId: { type: Schema.Types.ObjectId, ref: 'Workspace', required: true },
}, { timestamps: true, toJSON: { virtuals: true }, toObject: { virtuals: true } });

export const Board = mongoose.model<IBoard>('Board', BoardSchema);