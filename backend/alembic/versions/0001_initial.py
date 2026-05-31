from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("turns", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "evaluation_jobs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("conversation_id", sa.String(length=64), sa.ForeignKey("conversations.id"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("progress", sa.Float(), nullable=False),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("result_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "turn_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("evaluation_jobs.id"), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("context_analysis", sa.JSON(), nullable=False),
        sa.Column("routed_facets", sa.JSON(), nullable=False),
        sa.Column("consistency_alerts", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "facet_scores",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("turn_result_id", sa.Integer(), sa.ForeignKey("turn_results.id"), nullable=False),
        sa.Column("facet_id", sa.String(length=64), nullable=False),
        sa.Column("facet_name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=16), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("confidence_interval", sa.JSON(), nullable=False),
        sa.Column("agreement_score", sa.Float(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("adjustment", sa.Text(), nullable=False),
        sa.Column("raw_outputs", sa.JSON(), nullable=False),
        sa.Column("review_flags", sa.JSON(), nullable=False),
    )
    op.create_index("ix_conversations_title", "conversations", ["title"])
    op.create_index("ix_evaluation_jobs_status", "evaluation_jobs", ["status"])
    op.create_index("ix_turn_results_job_id", "turn_results", ["job_id"])
    op.create_index("ix_turn_results_turn_index", "turn_results", ["turn_index"])
    op.create_index("ix_facet_scores_turn_result_id", "facet_scores", ["turn_result_id"])
    op.create_index("ix_facet_scores_facet_id", "facet_scores", ["facet_id"])
    op.create_index("ix_facet_scores_domain", "facet_scores", ["domain"])

def downgrade() -> None:
    op.drop_table("facet_scores")
    op.drop_table("turn_results")
    op.drop_table("evaluation_jobs")
    op.drop_table("conversations")
