def build_critique_prompt(
    my_name: str,
    my_draft: str,
    other_drafts: dict[str, str],
) -> str:
    others_block = "\n\n".join(
        f"--- Draft by {name} ---\n{draft}" for name, draft in other_drafts.items()
    )
    return f"""You are {my_name}, an expert educator reviewing question papers drafted by peer AI models.

YOUR OWN DRAFT:
--- Your Draft ({my_name}) ---
{my_draft}

PEER DRAFTS FOR REVIEW:
{others_block}

Your task:
1. Critically evaluate EACH peer draft — identify strong questions worth keeping, weak or ambiguous questions, topic gaps, and difficulty imbalances
2. Compare against your own draft and acknowledge where peers did better
3. Propose specific improvements: reworded questions, missing topics, better mark distribution
4. Keep your critique concise and constructive — bullet points preferred

Your critique will be used by the synthesiser to build the final best paper."""
