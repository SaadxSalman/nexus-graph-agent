// client/components/editor.tsx
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

export const DescriptionEditor = ({ content }: { content: string }) => {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content,
    editorProps: {
      attributes: { class: "prose dark:prose-invert max-w-none focus:outline-none" }
    }
  });
  return <EditorContent editor={editor} className="border p-3 rounded-md min-h-[150px]" />;
};