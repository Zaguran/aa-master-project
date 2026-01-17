-- Migration: Add id_type column to nodes table
-- Version: 1.65
-- Author: Claude Code
-- Date: 2026-01-17

-- Add id_type column
ALTER TABLE work_aa.nodes
ADD COLUMN IF NOT EXISTS id_type TEXT;

-- Add check constraint
ALTER TABLE work_aa.nodes
ADD CONSTRAINT check_id_type
CHECK (id_type IN ('requirement', 'information') OR id_type IS NULL);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_nodes_id_type
ON work_aa.nodes(id_type);

-- Update existing records (default to 'requirement')
UPDATE work_aa.nodes
SET id_type = 'requirement'
WHERE id_type IS NULL;

-- Make column NOT NULL after backfill
ALTER TABLE work_aa.nodes
ALTER COLUMN id_type SET NOT NULL;

-- Migration complete
COMMENT ON COLUMN work_aa.nodes.id_type IS 'Type of node ID: requirement or information';
