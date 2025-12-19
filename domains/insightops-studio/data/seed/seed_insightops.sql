-- InsightOps Studio seed data (CD2.2)
-- Provides deterministic demo data for KPI snapshots, engagement signals, and executive summaries.

-- KPI daily snapshots
INSERT INTO io_kpi_daily (id, kpi_date, org_id, metric_key, metric_value, metric_unit, region, segment, channel, product, source, created_at, updated_at) VALUES
  ('3a9e8f5a-6f75-4f84-94ef-2e6eb7e8f111', '2024-05-01', 'demo_org', 'revenue', 125000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('5c0f5b84-0d8f-4fc8-8b53-8384c8a4a112', '2024-05-01', 'demo_org', 'pipeline', 310000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('7e9b1f2c-9d75-4c39-8f10-2b6d7f8a1a13', '2024-05-01', 'demo_org', 'win_rate', 32.5, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('2a7d3e58-1c64-4f36-b938-4d6b98b8c114', '2024-05-03', 'demo_org', 'revenue', 132500.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('9d1f2b4c-3e7a-4b6c-9d10-5f1e2c6d4b15', '2024-05-03', 'demo_org', 'pipeline', 320000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c16', '2024-05-03', 'demo_org', 'win_rate', 33.2, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e17', '2024-05-05', 'demo_org', 'revenue', 140000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('2e3f4a5b-6c7d-8e9f-0a1b-2c3d4e5f6a18', '2024-05-05', 'demo_org', 'pipeline', 330000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('3f4a5b6c-7d8e-9f0a-1b2c-3d4e5f6a7b19', '2024-05-05', 'demo_org', 'win_rate', 34.0, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('4b5c6d7e-8f90-1a2b-3c4d-5e6f7a8b9c20', '2024-05-07', 'demo_org', 'revenue', 150500.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('5c6d7e8f-901a-2b3c-4d5e-6f7a8b9c0d21', '2024-05-07', 'demo_org', 'pipeline', 342000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('6d7e8f90-1a2b-3c4d-5e6f-7a8b9c0d1e22', '2024-05-07', 'demo_org', 'win_rate', 34.8, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('7e8f901a-2b3c-4d5e-6f7a-8b9c0d1e2f23', '2024-05-09', 'demo_org', 'revenue', 158000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('8f901a2b-3c4d-5e6f-7a8b-9c0d1e2f3a24', '2024-05-09', 'demo_org', 'pipeline', 355000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('9a0b1c2d-3e4f-5a6b-7c8d-9e0f1a2b3c25', '2024-05-09', 'demo_org', 'win_rate', 35.4, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('0b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d26', '2024-05-11', 'demo_org', 'revenue', 164500.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('1d2e3f4a-5b6c-7d8e-9f0a-1b2c3d4e5f27', '2024-05-11', 'demo_org', 'pipeline', 365000.00, 'USD', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('2f304152-6374-8596-a7b8-c9d0e1f22328', '2024-05-11', 'demo_org', 'win_rate', 36.1, '%', 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW());

-- Engagement signals
INSERT INTO io_engagement_signal_daily (id, signal_date, org_id, signal_key, signal_value, region, segment, channel, product, source, created_at, updated_at) VALUES
  ('a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c31', '2024-05-01', 'demo_org', 'touches', 240, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d32', '2024-05-01', 'demo_org', 'replies', 72, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e33', '2024-05-01', 'demo_org', 'meetings', 18, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f34', '2024-05-03', 'demo_org', 'touches', 255, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a35', '2024-05-03', 'demo_org', 'replies', 78, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f9a0b36', '2024-05-03', 'demo_org', 'meetings', 20, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('0c1d2e3f-4a5b-6c7d-8e9f-0a1b2c3d4e37', '2024-05-05', 'demo_org', 'touches', 268, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('1d2e3f4a-5b6c-7d8e-9f0a-1b2c3d4e5f38', '2024-05-05', 'demo_org', 'replies', 81, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('2e3f4a5b-6c7d-8e9f-0a1b-2c3d4e5f6a39', '2024-05-05', 'demo_org', 'meetings', 22, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('3f4a5b6c-7d8e-9f0a-1b2c-3d4e5f6a7b40', '2024-05-07', 'demo_org', 'touches', 282, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('4a5b6c7d-8e9f-0a1b-2c3d-4e5f6a7b8c41', '2024-05-07', 'demo_org', 'replies', 86, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('5b6c7d8e-9f0a-1b2c-3d4e-5f6a7b8c9d42', '2024-05-07', 'demo_org', 'meetings', 23, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('6c7d8e9f-0a1b-2c3d-4e5f-6a7b8c9d0e43', '2024-05-09', 'demo_org', 'touches', 295, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('7d8e9f0a-1b2c-3d4e-5f6a-7b8c9d0e1f44', '2024-05-09', 'demo_org', 'replies', 90, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('8e9f0a1b-2c3d-4e5f-6a7b-8c9d0e1f2a45', '2024-05-09', 'demo_org', 'meetings', 24, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('9f0a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b46', '2024-05-11', 'demo_org', 'touches', 310, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c47', '2024-05-11', 'demo_org', 'replies', 94, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW()),
  ('1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d48', '2024-05-11', 'demo_org', 'meetings', 25, 'NA', 'Enterprise', 'Direct', 'Core', 'seed', NOW(), NOW());

-- Executive summaries
INSERT INTO io_exec_summary (id, period_start, period_end, org_id, summary_type, summary_text, model_name, created_at, updated_at) VALUES
  ('c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e51', '2024-05-01', '2024-05-07', 'demo_org', 'manager', 'Week 1 snapshot: steady revenue growth with improving win rates and responsive engagement.', NULL, NOW(), NOW()),
  ('d2e3f4a5-b6c7-8d9e-0f1a-2b3c4d5e6f52', '2024-05-03', '2024-05-11', 'demo_org', 'board', 'Week 2 snapshot: pipeline expansion, higher meetings volume, and rising close ratios.', NULL, NOW(), NOW());
