// client/components/error-boundary.tsx
'use client';

export default function TaskErrorBoundary({ error, reset }: { error: Error, reset: () => void }) {
  return (
    <div className="p-4 border border-destructive rounded-md bg-destructive/10">
      <p className="text-sm">Failed to load this task.</p>
      <button onClick={() => reset()} className="text-xs underline">Retry</button>
    </div>
  );
}