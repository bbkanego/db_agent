# ── Input Schema ───────────────────────────────────────────────
from typing import List, Optional

from pydantic import BaseModel, Field


class SqlReviewInput(BaseModel):
    sql_code: str = Field(..., description="The SQL query or statement(s) to review")
    dialect: str = Field(
        default="Standard SQL",
        description="SQL dialect: e.g. 'PostgreSQL', 'BigQuery', 'MySQL', 'Standard SQL'"
    )
    schema_info: Optional[str] = Field(
        default=None,
        description="Optional: Table names, columns, types, PK/FK (helps logic review)"
    )


# ── Structured Output Schema ───────────────────────────────────
class SqlReviewOutput(BaseModel):
    syntax_issues: List[str] = Field(
        default_factory=list,
        description="Syntax errors / invalid constructs that would fail parsing"
    )
    logic_issues: List[str] = Field(
        default_factory=list,
        description="Logical bugs, anti-patterns, risky behavior, performance concerns"
    )
    severity_summary: str = Field(
        description="Overall: 'Clean', 'Minor issues', 'Medium risk', 'High risk / broken'"
    )
    suggested_fix: Optional[str] = Field(
        default=None,
        description="Improved / corrected version of the SQL (if changes needed)"
    )
    explanation: str = Field(
        description="Concise reasoning for the findings"
    )