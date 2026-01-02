// client/app/api/uploadthing/core.ts
import { createUploadthing, type FileRouter } from "uploadthing/next";
 
const f = createUploadthing();
 
export const ourFileRouter = {
  taskAttachment: f({ image: { maxFileSize: "4MB" }, pdf: { maxFileSize: "16MB" } })
    .middleware(async ({ req }) => {
      // Logic to check if user is logged in
      return { userId: "user_id" };
    })
    .onUploadComplete(async ({ metadata, file }) => {
      console.log("Upload complete for userId:", metadata.userId);
      console.log("file url", file.url);
    }),
} satisfies FileRouter;
 
export type OurFileRouter = typeof ourFileRouter;