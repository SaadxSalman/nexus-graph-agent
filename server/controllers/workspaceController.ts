export const getWorkspaceDetails = async (workspaceId: string) => {
  return await Workspace.aggregate([
    { $match: { _id: new mongoose.Types.ObjectId(workspaceId) } },
    {
      $lookup: {
        from: 'boards',
        localField: '_id',
        foreignField: 'workspaceId',
        as: 'boards',
      },
    },
    {
      $lookup: {
        from: 'users',
        localField: 'members',
        foreignField: '_id',
        as: 'memberDetails',
      },
    },
  ]);
};

export const getTaskWithUser = async (taskId: string) => {
  return await Task.findById(taskId)
    .populate('assignee', 'name email image') // Only fetch these fields
    .exec();
};