// server/validation/taskSchema.js
import { z } from 'zod';

export const taskSchema = z.object({
  title: z.string().min(3).max(100),
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE']),
});

// Middleware usage
export const validate = (schema) => (req, res, next) => {
  const result = schema.safeParse(req.body);
  if (!result.success) return res.status(400).json(result.error);
  next();
};