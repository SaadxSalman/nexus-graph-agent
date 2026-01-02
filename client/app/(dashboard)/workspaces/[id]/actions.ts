// client/app/(dashboard)/workspaces/[id]/actions.ts
'use server'
import { revalidatePath } from 'next/cache';

export async function createTask(formData: FormData) {
  const title = formData.get("title");
  const boardId = formData.get("boardId");

  // Call MongoDB via Mongoose directly here
  await db.tasks.create({ title, boardId });
  
  // Clear the cache for this specific board
  revalidatePath(`/workspaces/${boardId}`);
}