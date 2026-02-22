"use server";

import { PrismaClient } from "@prisma/client";
import { revalidatePath } from "next/cache";

// 1. Ensure Prisma is a Singleton
// This prevents exhausting your MongoDB connection pool during development
const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ["query"], // Useful for debugging "The Pulse" during dev
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

/**
 * Creates a new task in the database.
 * @param formData - The form data from the client
 * @param workspaceId - The specific tenant ID this task belongs to
 */
export async function createTaskAction(formData: FormData, workspaceId: string) {
  const title = formData.get("title") as string;

  // Validation
  if (!title || title.trim() === "") {
    return { success: false, error: "Task title is required" };
  }

  if (!workspaceId) {
    return { success: false, error: "Tenant Context (WorkspaceId) missing" };
  }

  try {
    const newTask = await prisma.task.create({
      data: {
        title: title.trim(),
        status: "TODO",
        priority: "MEDIUM",
        // Connect to existing workspace via ID
        workspace: {
          connect: { id: workspaceId },
        },
      },
    });

    // Clear Next.js cache for the dashboard so the new task appears
    revalidatePath("/");

    return { 
      success: true, 
      task: JSON.parse(JSON.stringify(newTask)) // Ensure POJO for Client Components
    };
  } catch (error: any) {
    console.error("❌ Prisma Action Error:", error.message);
    
    // Check if it's a connection error specifically
    if (error.code === 'P1001') {
      return { success: false, error: "Cannot reach MongoDB. Check your IP whitelist." };
    }

    return { success: false, error: "Database transaction failed." };
  }
}