// server/middleware/roleMiddleware.js
export const authorize = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ message: 'Permission denied' });
    }
    next();
  };
};

// Usage: router.delete('/task/:id', protect, authorize('admin', 'owner'), deleteTask);