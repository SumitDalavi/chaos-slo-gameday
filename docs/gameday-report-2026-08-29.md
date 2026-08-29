# Chaos Game Day Report
**Date:** 2026-08-29  
**Target System:** `distributed-job-scheduler`  
**Scenario:** Unplanned Worker Node Termination Mid-Execution

## 1. Hypothesis
When a worker node executing a critical job is forcefully killed (`kill -9`) before committing the result to the database:
1. The Postgres Advisory Lock for that job will be released immediately as the TCP connection drops.
2. The leader node will detect the abandoned job during its next sweep (within 5 seconds).
3. The job will be reassigned to a healthy worker and completed.
4. The job will be executed **exactly once** from a business logic perspective (the transaction will commit only once).

## 2. Preparation
- Spun up the `distributed-job-scheduler` via Docker Compose (1 Leader, 3 Workers, 1 PostgreSQL instance).
- Deployed a synthetic job designed to sleep for 30 seconds before committing to simulate a long-running process.

## 3. Execution (The Game Day)
**10:00:00** - Submitted job `job-uuid-1234`.
**10:00:02** - Verified via database that `worker-2` acquired the advisory lock and began execution.
**10:00:15** - Manually killed the `worker-2` container:
```bash
docker stop -t 0 distributed-job-scheduler-worker-2-1
```
**10:00:16** - Connection dropped. Postgres released advisory lock.
**10:00:20** - Leader node health check sweep detected `job-uuid-1234` in `RUNNING` state but with no active lock.
**10:00:20** - Leader reset job to `PENDING`.
**10:00:21** - `worker-3` picked up the job and acquired the advisory lock.
**10:00:51** - `worker-3` successfully completed the job and committed the transaction.

## 4. Observations & Results
- **Recovery Time:** 5 seconds to detect and reassign.
- **Data Integrity:** The transaction was committed exactly once. No duplicate data was generated.
- **Result:** ✅ **PASSED**

## 5. Action Items
- **Improvement:** The 5-second sweep is sufficient, but can be optimized to 2 seconds if job throughput increases, though this trades off CPU on the Postgres leader.
- **Monitoring:** Add a Prometheus alert `JobAbandonedRate` that fires if this happens more than 3 times an hour, as it indicates underlying infrastructure instability.
