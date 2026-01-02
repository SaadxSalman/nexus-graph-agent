// client/utils/date-formatter.ts
export const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(date);
};

// client/__tests__/utils.test.ts
import { formatDate } from '../utils/date-formatter';

test('formats date correctly for task cards', () => {
  const date = new Date('2026-01-02');
  expect(formatDate(date)).toBe('Jan 2');
});