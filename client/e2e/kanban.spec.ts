// client/e2e/kanban.spec.ts
import { test, expect } from '@playwright/test';

test('should move a task card between columns', async ({ page }) => {
  await page.goto('/workspaces/1');
  const task = page.locator('[data-testid="task-1"]');
  const targetColumn = page.locator('[data-testid="column-todo"]');
  
  await task.dragTo(targetColumn);
  
  // Verify the move persisted or UI updated
  await expect(targetColumn).toContainText('New Task Title');
});