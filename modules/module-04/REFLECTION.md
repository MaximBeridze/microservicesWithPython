# Module 4 — Reflection

**Team name**: _______________
**Branch**: `module-04/<team-name>`
**Submitted**: before Module 5 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

In Module 3, services called each other directly over HTTP. Now activity-service drops a message into a broker and moves on — it never waits for a reply.

**What does the activity-service gain by not waiting? And what does the notification-service gain by consuming at its own pace?**

Think about what happens under load, or when notification-service is temporarily down.

Activity-service can finish the request faster because it does not wait for notification-service. It saves the activity, publishes a message, and moves on.

Notification-service gains the ability to process messages at its own pace. If it is slow or temporarily down, RabbitMQ can hold the messages until it is ready.

---

## 2. Your choice

In Module 3 you already knew how to call another service directly over HTTP — you did it for user validation and game enrichment.

**Why not use the same approach for notifications? What does introducing a broker give you that a direct HTTP call doesn't?**

Think about what happens if notification-service is slow, or crashes mid-message.

Notifications do not need to happen immediately for the activity to be valid. A direct HTTP call would make activity creation depend on notification-service being online and fast.

A broker separates the two services. Activity-service only says “an activity happened,” and notification-service handles the notification later. This is different from user validation, which must happen before saving the activity.

A faster process also enhances user experience, the user doesn't have to wait for the notification to process before being able to continue.

---

## 3. The tradeoff

With synchronous REST, you get an immediate answer: success or failure. With async messaging, the activity is saved and the message is sent — but you have no idea if the notification was ever delivered.

**How would a user know if their notification was never sent? How would you know as a developer?**

What visibility do you lose when you go async?

The tradeoff is less immediate feedback. With REST, activity-service knows right away if notification-service succeeded or failed. With async messaging, it only knows that it published a message.

A user might only notice when a notification never appears - or if the notification is shown as a banner notification after it is processed. As a developer, I would need logs, queue monitoring, retries, or dead-letter queues to see what went wrong.

---

*Keep this file. You will refer back to it during the oral presentation.*
