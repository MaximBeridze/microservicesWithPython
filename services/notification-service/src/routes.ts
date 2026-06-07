import { Router, Request, Response } from "express";
import db from "./db";

const router = Router();

router.get("/v1/notifications", (_req: Request, res: Response) => {
  const notifications = db.prepare(
    "SELECT * FROM notifications ORDER BY received_at DESC"
  ).all();
  res.json(notifications);
});

router.get("/v1/notifications/:user_id", (req: Request, res: Response) => {
  const notifications = db.prepare(
    "SELECT * FROM notifications WHERE user_id = ? ORDER BY received_at DESC"
  ).all(req.params.user_id);
  res.json(notifications);
});

export default router;
