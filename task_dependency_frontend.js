import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Use the Vercel environment variable
const API_URL = import.meta.env.VITE_API_URL;

export default function TaskDependencyTracker() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/tasks`)  // Use dynamic API URL
      .then((res) => res.json())
      .then((data) => {
        setTasks(data);
        setLoading(false);
      });
  }, []);

  const updateTaskStatus = (taskId, newStatus) => {
    fetch(`${API_URL}/update_task`, {  // Use dynamic API URL
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: taskId, status: newStatus })
    })
      .then((res) => res.json())
      .then(() => {
        setTasks(tasks.map(task => 
          task.task_id === taskId ? { ...task, status: newStatus } : task
        ));
      });
  };

  if (loading) return <p>Loading tasks...</p>;

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      {tasks.map((task) => (
        <Card key={task.task_id} className="p-4 border">
          <CardContent>
            <h3 className="text-lg font-semibold">{task.task_name}</h3>
            <p className="text-sm">Phase: {task.phase}</p>
            <p className="text-sm">Status: <strong>{task.status}</strong></p>
            <p className="text-sm">Dependencies: {task.dependency || "None"}</p>
            {task.issue_flagged === "Yes" && (
              <p className="text-red-500">⚠ Issue: {task.resolution}</p>
            )}
            <div className="mt-4 space-x-2">
              <Button onClick={() => updateTaskStatus(task.task_id, "Complete")}>
                Mark as Complete
              </Button>
              <Button onClick={() => updateTaskStatus(task.task_id, "Incomplete")} variant="destructive">
                Mark as Incomplete
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
