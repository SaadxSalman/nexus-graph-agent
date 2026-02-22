"use server";

import { PrismaClient } from "@prisma/client";

// Prisma Singleton to prevent multiple instances in development
const globalForPrisma = global as unknown as { prisma: PrismaClient };
export const prisma = globalForPrisma.prisma || new PrismaClient();
if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

export async function createTaskAction(formData: FormData) {
  const title = formData.get("title") as string;
  
  if (!title) return { success: false, error: "Title is required" };

  try {
    const newTask = await prisma.task.create({
      data: {
        title,
        status: "TODO",
        priority: "MEDIUM",
        workspaceId: "65cb7f123456789012345678", // Ensure this is a valid MongoID
      },
    });
    return { success: true, task: newTask };
  } catch (e) {
    console.error("Action Error:", e);
    return { success: false, error: "Database Connection Failed" };
  }
}