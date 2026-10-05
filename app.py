import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import re
from difflib import SequenceMatcher


# ---------------------------------------------------
# SECTION 1: CONFIGURE STREAMLIT PAGE
# ---------------------------------------------------
# This controls the overall browser page and layout.
# "wide" gives us more room for dashboard cards and charts.

st.set_page_config(
    page_title="TradeIQ",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# END SECTION 1
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 2: CUSTOM DASHBOARD STYLING
# ---------------------------------------------------
# This CSS gives the app a cleaner dashboard-style layout.
# We keep the styling simple so it remains easy to maintain.

st.markdown(
    """
    <style>
        /* ---------------------------------------------------
           GLOBAL PAGE SPACING
           --------------------------------------------------- */

        .block-container {
            /* Keep page content below Streamlit's fixed top toolbar. */
            padding-top: 4.25rem;
            padding-bottom: 2rem;
            padding-left: 1.8rem;
            padding-right: 1.8rem;
            max-width: 1480px;
        }

        .dashboard-title {
            font-size: clamp(1.9rem, 2.5vw, 2.55rem);
            font-weight: 750;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            text-align: center;
        }

        .dashboard-subtitle {
            color: #9ca3af;
            font-size: clamp(0.85rem, 1vw, 1rem);
            margin-bottom: 1.1rem;
        }

        .section-label {
            font-size: clamp(1.05rem, 1.35vw, 1.28rem);
            font-weight: 720;
            margin-top: 0.25rem;
            margin-bottom: 0.7rem;
        }


        /* ---------------------------------------------------
           RESPONSIVE TILE GRID
           ---------------------------------------------------
           auto-fit allows the cards to automatically resize
           and wrap based on available browser width.
           --------------------------------------------------- */

        .tile-grid {
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(min(100%, 220px), 1fr)
            );
            gap: 14px;
            width: 100%;
        }

        .tile-grid-compact {
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(min(100%, 180px), 1fr)
            );
            gap: 12px;
            width: 100%;
        }

        .tile {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 13px;
            padding: clamp(13px, 1.3vw, 18px);
            min-height: 96px;
            background: rgba(255,255,255,0.022);
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-sizing: border-box;
        }

        .tile-label {
            color: #aeb6c2;
            font-size: clamp(0.76rem, 0.85vw, 0.88rem);
            margin-bottom: 0.4rem;
            line-height: 1.2;
        }

        .tile-value {
            font-size: clamp(1.35rem, 2vw, 1.95rem);
            font-weight: 680;
            line-height: 1.08;
            overflow-wrap: anywhere;
        }

        .tile-note {
            margin-top: 0.45rem;
            font-size: clamp(0.72rem, 0.78vw, 0.82rem);
            color: #8f98a5;
            line-height: 1.3;
        }


        /* ---------------------------------------------------
           CAMPAIGN HEALTH
           ---------------------------------------------------
           Health rows are intentionally more compact than
           standard KPI tiles so this panel does not become
           unnecessarily tall.
           --------------------------------------------------- */

        .health-card {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 13px;
            padding: 13px 15px;
            background: rgba(255,255,255,0.022);
            margin-bottom: 10px;
        }

        .health-label {
            color: #aeb6c2;
            font-size: 0.78rem;
            margin-bottom: 0.28rem;
        }

        .health-value {
            font-size: clamp(1.08rem, 1.45vw, 1.5rem);
            font-weight: 700;
            line-height: 1.15;
        }

        .status-good {
            color: #47d18c;
        }

        .status-warn {
            color: #f0b95a;
        }

        .status-bad {
            color: #ff6b6b;
        }


        /* ---------------------------------------------------
           KEY INSIGHTS
           --------------------------------------------------- */

        .insight-box {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 13px;
            padding: clamp(14px, 1.4vw, 19px);
            background: rgba(255,255,255,0.022);
        }

        .insight-list {
            margin: 0;
            padding-left: 1.15rem;
        }

        .insight-list li {
            margin-bottom: 0.72rem;
            line-height: 1.45;
            font-size: clamp(0.82rem, 0.92vw, 0.96rem);
        }

        .insight-list li:last-child {
            margin-bottom: 0;
        }

        .insight-green {
            color: #47d18c;
            font-weight: 600;
        }

        .insight-yellow {
            color: #f0b95a;
            font-weight: 600;
        }

        .insight-red {
            color: #ff6b6b;
            font-weight: 600;
        }


        /* ---------------------------------------------------
           SIDEBAR
           --------------------------------------------------- */

        /* Keep the sidebar fixed at a comfortable width and make it
           occupy the complete browser height. */
        /* Sidebar base styling. Do NOT force width here because Streamlit
           must be able to remove the sidebar from layout when collapsed. */
        section[data-testid="stSidebar"],
        div[data-testid="stSidebar"] {
            height: 100vh !important;
            min-height: 100vh !important;
            border-right: 1px solid rgba(255,255,255,0.10);
            background: rgba(28, 32, 43, 0.98);
        }

        /* Apply the preferred 360px width only while the sidebar is visible.
           :not([aria-expanded="false"]) also works with Streamlit builds where
           aria-expanded is absent in the normal expanded state. */
        section[data-testid="stSidebar"]:not([aria-expanded="false"]),
        div[data-testid="stSidebar"]:not([aria-expanded="false"]) {
            min-width: 360px !important;
            max-width: 360px !important;
            width: 360px !important;
        }

        /* Streamlit's sidebar content wrapper.  Using this selector makes
           the layout work across newer Streamlit versions as well. */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
        div[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {
            min-height: 100vh !important;
            height: 100vh !important;
            padding: 2.0rem 1.5rem 1.5rem 1.5rem !important;
            box-sizing: border-box !important;
            overflow-y: auto;
        }

        section[data-testid="stSidebar"] h2,
        div[data-testid="stSidebar"] h2 {
            font-size: 1.35rem;
            margin-top: 0 !important;
            margin-bottom: 1.0rem !important;
        }

        section[data-testid="stSidebar"] .stSelectbox,
        div[data-testid="stSidebar"] .stSelectbox {
            margin-bottom: 0.35rem !important;
        }

        section[data-testid="stSidebar"] hr,
        div[data-testid="stSidebar"] hr {
            margin-top: 1.35rem !important;
            margin-bottom: 1.35rem !important;
        }

        /* Keep both Navigation and Optimization groups compact so every
           option remains visible in the sidebar without being pushed below
           the viewport. */
        section[data-testid="stSidebar"] .stRadio,
        div[data-testid="stSidebar"] .stRadio {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"],
        div[data-testid="stSidebar"] div[role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            gap: 0.15rem !important;
            padding-bottom: 0.25rem !important;
            box-sizing: border-box !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label,
        div[data-testid="stSidebar"] div[role="radiogroup"] > label {
            min-height: 34px !important;
            margin: 0 !important;
            padding: 0.2rem 0 !important;
            font-size: 0.96rem !important;
            display: flex !important;
            align-items: center !important;
        }

        /* ---------------------------------------------------
           RESPONSIVE BREAKPOINTS
           --------------------------------------------------- */

        @media (max-width: 1100px) {
            .block-container {
                padding-left: 1.35rem;
                padding-right: 1.35rem;
            }

            .tile-grid {
                grid-template-columns: repeat(
                    auto-fit,
                    minmax(min(100%, 190px), 1fr)
                );
            }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 0.9rem;
                padding-right: 0.9rem;
                padding-top: 3.75rem;
            }

            .tile-grid,
            .tile-grid-compact {
                grid-template-columns: 1fr;
            }

            .tile {
                min-height: 82px;
            }

            .dashboard-title {
                margin-top: 0.2rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# END SECTION 2
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 3: UPLOAD + INTERPRET THE CAMPAIGN REPORT
# ---------------------------------------------------
# TradeIQ first tries to identify uploaded columns automatically.
# The user can then review/override every mapping before analysis begins.
# This makes the tool portable across reports from different DSPs/ad servers
# without forcing the source report to use TradeIQ's exact header names.

st.sidebar.markdown("## TradeIQ")
# TradeIQ brand stays above the Report Upload control.
st.markdown(
    '<div class="dashboard-title">TradeIQ</div>',
    unsafe_allow_html=True
)

# Keep report controls compact after upload/mapping is complete.
# The user can reopen this section at any time to replace the report or edit mappings.
report_setup_complete = st.session_state.get("_tradeiq_report_setup_complete", False)

with st.expander(
    "Report Upload",
    expanded=not report_setup_complete
):
    uploaded_file = st.file_uploader(
        "Upload Campaign Report",
        type=["xlsx", "xls"],
        help="Upload a campaign report. TradeIQ will suggest column mappings and let you correct them."
    )

    # Canonical fields understood by TradeIQ.
    # Only Date and Campaign_Name are universally required to establish campaign/date context.
    # Every other report field can be explicitly left as "Not mapped" when it is not
    # relevant to the uploaded campaign/report (for example Creative_Length_Sec for display).
    TRADEIQ_FIELDS = [
        "Date", "Campaign_Name", "Line_Item_Name", "Flight_Budget_USD",
        "Spend_USD", "Impressions_Served", "Clicks", "Conv_View_Through",
        "Conv_Click_Through", "Revenue_Attributed_USD", "Completion_Rate_%",
        "Impressions_Viewable", "Audience_Segment", "Creative_Name",
        "Creative_Length_Sec", "Channel", "Deal_Type", "Device_Type", "Site_Domain"
    ]

    CORE_REQUIRED_FIELDS = ["Date", "Campaign_Name"]

    OPTIONAL_REPORT_FIELDS = [
        field for field in TRADEIQ_FIELDS
        if field not in CORE_REQUIRED_FIELDS
    ]

    OPTIONAL_METADATA_FIELDS = ["Funnel_Stage", "Primary_KPI", "Secondary_KPI"]
    MAPPABLE_FIELDS = TRADEIQ_FIELDS + OPTIONAL_METADATA_FIELDS

    # Human-readable descriptions shown beside the mapper.
    FIELD_DESCRIPTIONS = {
        "Date": "Reporting date / day",
        "Campaign_Name": "Campaign name",
        "Line_Item_Name": "Line item / ad group name",
        "Flight_Budget_USD": "Campaign or line-item flight budget",
        "Spend_USD": "Media spend / cost",
        "Impressions_Served": "Delivered impressions",
        "Clicks": "Clicks",
        "Conv_View_Through": "View-through / post-view conversions",
        "Conv_Click_Through": "Click-through / post-click conversions",
        "Revenue_Attributed_USD": "Attributed conversion revenue",
        "Completion_Rate_%": "Video completion rate / VCR",
        "Impressions_Viewable": "Viewable impressions",
        "Audience_Segment": "Audience / segment name",
        "Creative_Name": "Creative / ad name",
        "Creative_Length_Sec": "Creative duration in seconds",
        "Channel": "Media / inventory channel",
        "Deal_Type": "Open auction / PMP / PG / deal type",
        "Device_Type": "Device type",
        "Site_Domain": "Site / domain / publisher",
        "Funnel_Stage": "Awareness / consideration / conversion metadata",
        "Primary_KPI": "Primary campaign KPI metadata",
        "Secondary_KPI": "Secondary campaign KPI metadata"
    }

    # Known DSP/reporting aliases. These only create suggestions; the user remains
    # in control and can override any suggestion in the mapping UI.
    COLUMN_ALIASES = {
        "Date": ["date", "report date", "day", "event date", "activity date"],
        "Campaign_Name": ["campaign", "campaign name", "campaign_name", "campaign title"],
        "Line_Item_Name": [
            "line item", "line item name", "line_item_name", "ad group",
            "ad group name", "adgroup", "placement", "placement name"
        ],
        "Flight_Budget_USD": [
            "flight budget", "flight budget usd", "budget", "campaign budget",
            "line item budget", "total budget", "planned budget"
        ],
        "Spend_USD": [
            "spend", "spend usd", "media spend", "media cost", "cost",
            "total spend", "advertiser cost", "net media cost"
        ],
        "Impressions_Served": [
            "impressions", "impressions served", "imps", "served impressions",
            "total impressions"
        ],
        "Clicks": ["clicks", "total clicks", "click"],
        "Conv_View_Through": [
            "view through conversions", "view-through conversions",
            "view conversions", "vtc", "post view conversions",
            "post-view conversions", "view thru conversions"
        ],
        "Conv_Click_Through": [
            "click through conversions", "click-through conversions",
            "click conversions", "ctc", "post click conversions",
            "post-click conversions", "click thru conversions"
        ],
        "Revenue_Attributed_USD": [
            "revenue", "attributed revenue", "revenue attributed",
            "conversion revenue", "revenue usd", "sales revenue",
            "purchase revenue"
        ],
        "Completion_Rate_%": [
            "completion rate", "completion rate %", "video completion rate",
            "vcr", "video completion %", "video completion rate %"
        ],
        "Impressions_Viewable": [
            "viewable impressions", "impressions viewable", "viewable imps",
            "measurable viewable impressions"
        ],
        "Audience_Segment": [
            "audience", "audience segment", "segment", "audience name",
            "targeting segment", "data segment"
        ],
        "Creative_Name": [
            "creative", "creative name", "ad name", "creative_name",
            "creative title"
        ],
        "Creative_Length_Sec": [
            "creative length", "creative length sec", "creative duration",
            "video length", "duration seconds", "video duration",
            "creative duration seconds"
        ],
        "Channel": [
            "channel", "media channel", "inventory channel", "environment",
            "media type"
        ],
        "Deal_Type": [
            "deal type", "deal_type", "inventory deal type", "buy type",
            "transaction type"
        ],
        "Device_Type": [
            "device type", "device_type", "device", "device category"
        ],
        "Site_Domain": [
            "site domain", "domain", "domain name", "website", "website domain",
            "site", "publisher", "publisher name", "site publisher",
            "publisher domain", "app/site", "app or site"
        ],
        "Funnel_Stage": [
            "funnel stage", "funnel", "campaign funnel", "funnel_stage",
            "marketing funnel stage", "objective stage"
        ],
        "Primary_KPI": [
            "primary kpi", "primary_kpi", "main kpi", "primary metric",
            "main metric", "campaign kpi"
        ],
        "Secondary_KPI": [
            "secondary kpi", "secondary_kpi", "supporting kpi",
            "secondary metric", "supporting metric"
        ]
    }


    def normalize_column_name(value):
        """Normalize a header so case, spaces and punctuation do not affect matching."""
        return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


    def score_column_for_field(column, field):
        """Return the best similarity score between an uploaded column and a TradeIQ field."""
        column_norm = normalize_column_name(column)
        aliases = [field] + COLUMN_ALIASES.get(field, [])

        if not column_norm:
            return 0.0

        best_score = 0.0
        for alias in aliases:
            alias_norm = normalize_column_name(alias)

            if column_norm == alias_norm:
                return 1.0

            score = SequenceMatcher(None, column_norm, alias_norm).ratio()

            # Give a small boost when one normalized phrase contains the other.
            if alias_norm and (alias_norm in column_norm or column_norm in alias_norm):
                score = max(score, 0.90)

            best_score = max(best_score, score)

        return best_score


    def build_suggested_mapping(columns):
        """
        Build one-to-one automatic suggestions.
        Exact/alias matches are accepted first, then cautious fuzzy matches.
        The result maps TradeIQ field -> uploaded column.
        """
        uploaded_columns = list(columns)
        suggestions = {}
        confidence = {}
        method = {}
        used_columns = set()

        # Pass 1: exact canonical/alias matches.
        for field in MAPPABLE_FIELDS:
            ranked = sorted(
                (
                    (score_column_for_field(column, field), column)
                    for column in uploaded_columns
                    if column not in used_columns
                ),
                reverse=True
            )

            if ranked and ranked[0][0] >= 0.999:
                score, column = ranked[0]
                suggestions[field] = column
                confidence[field] = score
                method[field] = "Exact / Alias"
                used_columns.add(column)

        # Pass 2: cautious fuzzy suggestions.
        for field in MAPPABLE_FIELDS:
            if field in suggestions:
                continue

            ranked = sorted(
                (
                    (score_column_for_field(column, field), column)
                    for column in uploaded_columns
                    if column not in used_columns
                ),
                reverse=True
            )

            if ranked and ranked[0][0] >= 0.78:
                score, column = ranked[0]
                suggestions[field] = column
                confidence[field] = score
                method[field] = "Suggested"
                used_columns.add(column)

        return suggestions, confidence, method


    def mapping_key(field):
        """Stable Streamlit key for each mapping dropdown."""
        return "tradeiq_map_" + re.sub(r"[^a-zA-Z0-9_]+", "_", field)


    if uploaded_file is None:
        st.info("Upload an Excel campaign report to begin analysis.")
        st.stop()

    try:
        raw_uploaded_df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"TradeIQ could not read the uploaded Excel file: {exc}")
        st.stop()

    if raw_uploaded_df.empty:
        st.error("The uploaded Excel file does not contain any data rows.")
        st.stop()

    uploaded_columns = list(raw_uploaded_df.columns)
    suggested_mapping, mapping_confidence, mapping_method = build_suggested_mapping(
        uploaded_columns
    )

    # Reset mapping widgets when a different file is uploaded.
    file_signature = (
        uploaded_file.name,
        getattr(uploaded_file, "size", None),
        tuple(str(c) for c in uploaded_columns)
    )

    if st.session_state.get("_tradeiq_mapping_file_signature") != file_signature:
        st.session_state["_tradeiq_mapping_file_signature"] = file_signature

        for field in MAPPABLE_FIELDS:
            key = mapping_key(field)
            suggested_column = suggested_mapping.get(field)

            if suggested_column in uploaded_columns:
                st.session_state[key] = suggested_column
            else:
                st.session_state[key] = "— Not mapped —"

    # ---------------- USER-CONTROLLED COLUMN MAPPER ----------------
    st.markdown("### Metric / Column Mapping")
    st.caption(
        "TradeIQ suggests matches automatically. Review them and change any dropdown "
        "so each TradeIQ metric points to the correct column in your uploaded report."
    )

    mapping_options = ["— Not mapped —"] + uploaded_columns
    user_field_mapping = {}

    with st.expander("Review & Map Report Columns", expanded=True):
        st.caption(
            "Only Date and Campaign Name are always required. Any other field can stay "
            "Not mapped when it is not relevant to this campaign or is unavailable in the report."
        )

        for field in MAPPABLE_FIELDS:
            required_label = "Required" if field in CORE_REQUIRED_FIELDS else "Optional"
            suggested_column = suggested_mapping.get(field)
            score = mapping_confidence.get(field)

            selected_column = st.selectbox(
                f"{field}  •  {required_label}",
                options=mapping_options,
                key=mapping_key(field),
                help=FIELD_DESCRIPTIONS.get(field, field)
            )

            if selected_column != "— Not mapped —":
                user_field_mapping[field] = selected_column

            if suggested_column:
                confidence_text = f"{score:.0%}" if score is not None else ""
                st.caption(
                    f"Suggested: {suggested_column} "
                    f"({mapping_method.get(field, 'Suggested')}, {confidence_text})"
                )

    # Prevent one source column from silently feeding multiple canonical fields.
    selected_sources = list(user_field_mapping.values())
    duplicate_sources = sorted(
        {
            source
            for source in selected_sources
            if selected_sources.count(source) > 1
        }
    )

    if duplicate_sources:
        st.error(
            "Each uploaded column can only be mapped once. Duplicate selection(s): "
            + ", ".join(str(x) for x in duplicate_sources)
        )
        st.error(
            "Please fix the duplicate column mapping in the sidebar before TradeIQ runs."
        )
        st.stop()

    # Rename uploaded source columns to the canonical names used by the existing engine.
    # pandas.rename expects source -> target, so reverse the UI mapping.
    column_mapping = {
        source_column: tradeiq_field
        for tradeiq_field, source_column in user_field_mapping.items()
    }

    raw_df = raw_uploaded_df.rename(columns=column_mapping).copy()

    missing_fields = [
        field for field in CORE_REQUIRED_FIELDS
        if field not in raw_df.columns
    ]

    mapped_required_count = len(CORE_REQUIRED_FIELDS) - len(missing_fields)
    mapped_optional_report_count = sum(
        field in raw_df.columns for field in OPTIONAL_REPORT_FIELDS
    )
    mapped_optional_metadata_count = sum(
        field in raw_df.columns for field in OPTIONAL_METADATA_FIELDS
    )

    st.caption(
        f"Core mapped: {mapped_required_count}/{len(CORE_REQUIRED_FIELDS)}  •  "
        f"Optional report fields: {mapped_optional_report_count}/{len(OPTIONAL_REPORT_FIELDS)}  •  "
        f"Metadata: {mapped_optional_metadata_count}/{len(OPTIONAL_METADATA_FIELDS)}"
    )

    with st.expander("Mapping Summary", expanded=False):
        mapping_rows = []

        for field in MAPPABLE_FIELDS:
            selected = user_field_mapping.get(field)

            if selected:
                if selected == suggested_mapping.get(field):
                    match_type = mapping_method.get(field, "Selected")
                    score = mapping_confidence.get(field)
                    confidence_text = f"{score:.0%}" if score is not None else "—"
                else:
                    match_type = "Manual"
                    confidence_text = "User selected"

                mapping_rows.append({
                    "TradeIQ Field": field,
                    "Uploaded Column": selected,
                    "Status": match_type,
                    "Confidence": confidence_text
                })
            else:
                mapping_rows.append({
                    "TradeIQ Field": field,
                    "Uploaded Column": "Not mapped",
                    "Status": "Missing" if field in CORE_REQUIRED_FIELDS else "Optional / Not used",
                    "Confidence": "—"
                })

        st.dataframe(
            pd.DataFrame(mapping_rows),
            hide_index=True,
            use_container_width=True
        )

    if missing_fields:
        st.warning(
            "TradeIQ needs only the following core field(s) before it can continue: "
            + ", ".join(missing_fields)
        )
        st.stop()

    # Reaching this point means the file loaded and all universally required
    # mappings passed validation. Collapse this section on the next rerun.
    st.session_state["_tradeiq_report_setup_complete"] = True

# Compact report status remains visible while the full setup stays collapsed.
st.sidebar.caption(f"Report: {uploaded_file.name}")


# Create neutral placeholders for optional fields that the trader intentionally
# leaves unmapped. This prevents unrelated analyzers from crashing while still
# allowing each analyzer to decide whether it has enough relevant data to run.
NUMERIC_OPTIONAL_DEFAULTS = {
    "Flight_Budget_USD": np.nan,
    "Spend_USD": 0.0,
    "Impressions_Served": 0.0,
    "Clicks": 0.0,
    "Conv_View_Through": 0.0,
    "Conv_Click_Through": 0.0,
    "Revenue_Attributed_USD": 0.0,
    "Completion_Rate_%": np.nan,
    "Impressions_Viewable": 0.0,
    "Creative_Length_Sec": np.nan
}

TEXT_OPTIONAL_DEFAULTS = {
    "Line_Item_Name": "Not Available",
    "Audience_Segment": "Not Available",
    "Creative_Name": "Not Available",
    "Channel": "Not Available",
    "Deal_Type": "Not Available",
    "Device_Type": "Not Available",
    "Site_Domain": "Not Available"
}

for field, default_value in NUMERIC_OPTIONAL_DEFAULTS.items():
    if field not in raw_df.columns:
        raw_df[field] = default_value

for field, default_value in TEXT_OPTIONAL_DEFAULTS.items():
    if field not in raw_df.columns:
        raw_df[field] = default_value

raw_df["Date"] = pd.to_datetime(raw_df["Date"], errors="coerce")

# ---------------------------------------------------
# END SECTION 3
# ---------------------------------------------------


# ---------------------------------------------------
# DATA QUALITY & RECONCILIATION LAYER
# ---------------------------------------------------
# TradeIQ validates the raw report before any performance analysis.
# Only rows with a strong, explicit exclusion rule are removed from
# analytical calculations. Other unusual records remain in the clean
# dataset but are surfaced as warnings for investigation.

def apply_data_quality_rules(source_df):
    validated = source_df.copy()

    # Keep an immutable row reference so reconciliation records can always
    # be traced back to the source report.
    validated["Source_Row"] = np.arange(2, len(validated) + 2)

    numeric_columns = [
        "Spend_USD", "Impressions_Served", "Clicks",
        "Conv_View_Through", "Conv_Click_Through",
        "Revenue_Attributed_USD", "Impressions_Viewable"
    ]
    for column in numeric_columns:
        if column in validated.columns:
            validated[column] = pd.to_numeric(validated[column], errors="coerce")

    impressions_series = validated.get(
        "Impressions_Served", pd.Series(0, index=validated.index)
    ).fillna(0)
    spend_series = validated.get(
        "Spend_USD", pd.Series(0, index=validated.index)
    ).fillna(0)
    clicks_series = validated.get(
        "Clicks", pd.Series(0, index=validated.index)
    ).fillna(0)
    view_conv_series = validated.get(
        "Conv_View_Through", pd.Series(0, index=validated.index)
    ).fillna(0)
    click_conv_series = validated.get(
        "Conv_Click_Through", pd.Series(0, index=validated.index)
    ).fillna(0)
    revenue_series = validated.get(
        "Revenue_Attributed_USD", pd.Series(0, index=validated.index)
    ).fillna(0)
    total_conv_series = view_conv_series + click_conv_series

    # HARD EXCLUSION: spend with zero impressions is treated as ghost spend.
    # It is retained in reconciliation records but excluded from media spend
    # and every downstream analyzer.
    ghost_spend_mask = (spend_series > 0) & (impressions_series == 0)

    validated["Exclude_From_Analysis"] = ghost_spend_mask
    validated["Data_Quality_Status"] = "Valid"
    validated["Reconciliation_Reason"] = ""
    validated.loc[ghost_spend_mask, "Data_Quality_Status"] = "Reconciliation Required"
    validated.loc[ghost_spend_mask, "Reconciliation_Reason"] = (
        "Ghost Spend: Spend > 0 while Impressions = 0"
    )

    # Warning rules do not automatically remove data. They flag records that
    # deserve trader/ad-ops review without assuming the delivery is invalid.
    warning_reasons = pd.Series("", index=validated.index, dtype="object")

    def add_warning(mask, reason):
        nonlocal warning_reasons
        mask = mask.fillna(False) & ~ghost_spend_mask
        warning_reasons.loc[mask] = warning_reasons.loc[mask].apply(
            lambda existing: f"{existing}; {reason}" if existing else reason
        )

    add_warning(
        (impressions_series > 0) & (spend_series == 0),
        "Zero-cost delivery: Impressions > 0 while Spend = 0"
    )
    add_warning(
        clicks_series > impressions_series,
        "Data integrity: Clicks exceed Impressions"
    )
    add_warning(
        (total_conv_series > 0) & (impressions_series == 0),
        "Attribution check: Conversions recorded with zero Impressions"
    )
    add_warning(
        (revenue_series > 0) & (total_conv_series == 0),
        "Measurement check: Revenue recorded with zero Conversions"
    )

    negative_mask = pd.Series(False, index=validated.index)
    for column in numeric_columns:
        if column in validated.columns:
            negative_mask = negative_mask | (validated[column].fillna(0) < 0)
    add_warning(negative_mask, "Data integrity: Negative delivery or financial value")

    identifier_columns = [
        column for column in ["Campaign_Name", "Line_Item_Name"]
        if column in validated.columns
    ]
    if identifier_columns:
        missing_identifier_mask = pd.Series(False, index=validated.index)
        for column in identifier_columns:
            missing_identifier_mask = missing_identifier_mask | (
                validated[column].isna()
                | validated[column].astype(str).str.strip().eq("")
            )
        add_warning(missing_identifier_mask, "Missing campaign or line-item identifier")

    # Exact duplicate rows are flagged, not automatically deleted, because
    # repeated dimensional rows can sometimes be legitimate in DSP exports.
    source_columns = [
        column for column in source_df.columns
        if column in validated.columns
    ]
    duplicate_mask = validated[source_columns].duplicated(keep=False)
    add_warning(duplicate_mask, "Potential exact duplicate row")

    warning_mask = warning_reasons.ne("") & ~ghost_spend_mask
    validated.loc[warning_mask, "Data_Quality_Status"] = "Warning"
    validated.loc[warning_mask, "Reconciliation_Reason"] = warning_reasons.loc[warning_mask]

    clean = validated.loc[~validated["Exclude_From_Analysis"]].copy()
    return validated, clean


validated_df, df = apply_data_quality_rules(raw_df)

# ---------------------------------------------------
# END SECTION 3
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 4: SIDEBAR NAVIGATION AND CAMPAIGN CONTROLS
# ---------------------------------------------------
# The sidebar keeps navigation and campaign selection separate
# from the main dashboard content.

# Campaign selection appears after report upload so the user chooses
# the campaign before navigating to a specific analysis page.

campaign_list = sorted(
    validated_df["Campaign_Name"]
    .dropna()
    .unique()
)

selected_campaign = st.sidebar.selectbox(
    "Campaign",
    campaign_list
)

st.sidebar.markdown("---")

# Main navigation appears below the campaign selector.
# Optimization tools are grouped separately so the sidebar is easier to scan.

def _select_main_navigation():
    st.session_state["optimization_navigation"] = None
    st.session_state["comparison_navigation"] = None
    st.session_state["active_sidebar_group"] = "navigation"


def _select_optimization_navigation():
    # Optimization pages take over the active page without changing the
    # user's last standard Navigation selection.
    st.session_state["active_sidebar_group"] = "optimization"


def _select_comparison_navigation():
    st.session_state["active_sidebar_group"] = "comparison"


# Initialize which sidebar group currently controls the page.
if "active_sidebar_group" not in st.session_state:
    st.session_state["active_sidebar_group"] = "navigation"


navigation_page = st.sidebar.radio(
    "Navigation",
    [
        "Campaign Overview",
        "Data Quality / Reconciliation",
        "Monthly Trends",
        "Pacing & Delivery Analyzer",
        "Audience Analyzer",
        "Creative Analyzer",
        "Inventory Analyzer",
        "Domain / Website Analyzer"
    ],
    key="main_navigation",
    on_change=_select_main_navigation
)

# Keep Navigation active only when neither of the dedicated sidebar
# workspaces (Comparison or Optimization) is selected.
# Previously this checked only Optimization, which immediately reset
# Comparison back to Navigation and prevented Comparison Analysis from opening.
if (
    st.session_state.get("optimization_navigation") is None
    and st.session_state.get("comparison_navigation") is None
):
    st.session_state["active_sidebar_group"] = "navigation"

st.sidebar.markdown("---")

comparison_page = st.sidebar.radio(
    "Comparison",
    ["Comparison Analysis"],
    index=None,
    key="comparison_navigation",
    on_change=_select_comparison_navigation
)

st.sidebar.markdown("---")

optimization_page = st.sidebar.radio(
    "Optimization",
    [
        "Optimization Action Center",
        "Optimization Tracker"
    ],
    index=None,
    key="optimization_navigation",
    on_change=_select_optimization_navigation
)

if (
    st.session_state.get("active_sidebar_group") == "comparison"
    and comparison_page is not None
):
    page = comparison_page
elif (
    st.session_state.get("active_sidebar_group") == "optimization"
    and optimization_page is not None
):
    page = optimization_page
else:
    page = navigation_page

campaign_df = df[
    df["Campaign_Name"] == selected_campaign
].copy()

raw_campaign_df = validated_df[
    validated_df["Campaign_Name"] == selected_campaign
].copy()

reconciliation_df = raw_campaign_df[
    raw_campaign_df["Exclude_From_Analysis"]
].copy()

quality_warning_df = raw_campaign_df[
    raw_campaign_df["Data_Quality_Status"] == "Warning"
].copy()

reported_spend = raw_campaign_df.get(
    "Spend_USD", pd.Series(dtype=float)
).sum()
reconciliation_spend = reconciliation_df.get(
    "Spend_USD", pd.Series(dtype=float)
).sum()
valid_media_spend = campaign_df.get(
    "Spend_USD", pd.Series(dtype=float)
).sum()
data_quality_issue_count = len(reconciliation_df) + len(quality_warning_df)

# ---------------------------------------------------
# END SECTION 4
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 5: CAMPAIGN KPI + GOAL CONFIGURATION
# ---------------------------------------------------
# Report upload/mapping stays in the sidebar. Campaign strategy configuration
# belongs on the main screen so the sidebar remains focused on navigation.
#
# Workflow:
#   Upload -> Map report -> Select campaign -> Configure KPI goals -> Analyze
#
# If KPI metadata exists in the report, TradeIQ preselects it. Otherwise the
# trader selects it manually. ROAS is always available for every campaign.

def first_nonblank_value(data, column, default=None):
    if column not in data.columns:
        return default
    values = data[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return values.iloc[0] if not values.empty else default


def normalize_funnel_stage(value):
    if value is None:
        return "Not Assigned"
    value_text = str(value).strip().lower()
    if (
        "convert" in value_text
        or "conversion" in value_text
        or "performance" in value_text
        or "lower" in value_text
    ):
        return "Conversion"
    if (
        "aware" in value_text
        or "awareness" in value_text
        or "upper" in value_text
    ):
        return "Awareness"
    return str(value).strip().title() if str(value).strip() else "Not Assigned"


# ROAS is intentionally included for every campaign, regardless of funnel stage.
KPI_OPTIONS = [
    "CPA",
    "Completion Rate",
    "Viewability",
    "CTR",
    "CPM",
    "CPC",
    "Conversion Rate"
]

# ROAS is intentionally separate from the Primary/Secondary KPI dropdowns.
# Every campaign can have an independent ROAS target.
ROAS_KPI = "ROAS"

KPI_ALIASES = {
    "CPA": ["cpa", "cost per acquisition", "cost per action", "cost per conversion"],
    "ROAS": ["roas", "return on ad spend", "return on advertising spend"],
    "Completion Rate": [
        "completion rate", "video completion rate", "vcr",
        "video completion", "completed view rate"
    ],
    "Viewability": ["viewability", "viewable rate", "viewability rate"],
    "CTR": ["ctr", "click through rate", "click-through rate"],
    "CPM": ["cpm", "cost per mille", "cost per thousand"],
    "CPC": ["cpc", "cost per click"],
    "Conversion Rate": [
        "conversion rate", "conv rate", "cvr", "click conversion rate"
    ]
}


def normalize_kpi_name(value):
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    normalized = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()

    for canonical, aliases in KPI_ALIASES.items():
        for alias in [canonical] + aliases:
            alias_normalized = re.sub(
                r"[^a-z0-9]+", " ", str(alias).lower()
            ).strip()
            if normalized == alias_normalized:
                return canonical

    best_kpi = None
    best_score = 0.0
    for canonical, aliases in KPI_ALIASES.items():
        score = max(
            SequenceMatcher(
                None,
                normalized.replace(" ", ""),
                re.sub(r"[^a-z0-9]+", "", alias.lower())
            ).ratio()
            for alias in [canonical] + aliases
        )
        if score > best_score:
            best_score = score
            best_kpi = canonical

    return best_kpi if best_score >= 0.80 else None


def infer_funnel_from_kpis(primary, secondary=None):
    kpis = {primary, secondary}
    if "CPA" in kpis or "ROAS" in kpis or "Conversion Rate" in kpis:
        return "Conversion"
    if "Completion Rate" in kpis or "Viewability" in kpis or "CPM" in kpis:
        return "Awareness"
    return "Not Assigned"


def kpi_goal_help(kpi):
    help_text = {
        "CPA": "Maximum acceptable cost per acquisition in dollars. Lower is better.",
        "ROAS": "Minimum required return on ad spend. Example: 3.0 means 3x. Higher is better.",
        "Completion Rate": "Minimum desired video completion rate as a percentage. Example: 80.",
        "Viewability": "Minimum desired viewability percentage. Example: 70.",
        "CTR": "Minimum desired click-through rate percentage. Example: 0.20.",
        "CPM": "Maximum acceptable CPM in dollars. Lower is better.",
        "CPC": "Maximum acceptable cost per click in dollars. Lower is better.",
        "Conversion Rate": "Minimum desired conversion rate percentage. Higher is better."
    }
    return help_text.get(kpi, "Enter the campaign goal for this KPI.")


reported_funnel_stage = normalize_funnel_stage(
    first_nonblank_value(raw_campaign_df, "Funnel_Stage", "Not Assigned")
)
reported_primary_kpi_raw = first_nonblank_value(
    raw_campaign_df, "Primary_KPI", None
)
reported_secondary_kpi_raw = first_nonblank_value(
    raw_campaign_df, "Secondary_KPI", None
)

detected_primary_kpi = normalize_kpi_name(reported_primary_kpi_raw)
detected_secondary_kpi = normalize_kpi_name(reported_secondary_kpi_raw)

# ROAS is configured separately, so do not use it as a dropdown default.
if detected_primary_kpi == "ROAS":
    detected_primary_kpi = None
if detected_secondary_kpi == "ROAS":
    detected_secondary_kpi = None

# Store campaign-specific configuration so switching campaigns preserves each
# campaign's selected KPI/goal during the current Streamlit session.
campaign_key = re.sub(
    r"[^a-zA-Z0-9_]+",
    "_",
    str(selected_campaign)
).strip("_") or "campaign"

st.markdown(
    f"""
    <div class="dashboard-subtitle">
        {selected_campaign} &nbsp;•&nbsp; Configure campaign goals before analysis
    </div>
    """,
    unsafe_allow_html=True
)

config_state_key = f"kpi_config_{campaign_key}"
has_saved_kpi_config = config_state_key in st.session_state

if has_saved_kpi_config:
    saved_preview = st.session_state[config_state_key]
    preview_primary = saved_preview["primary_kpi"]
    preview_primary_goal = saved_preview["primary_goal"]
    preview_secondary = saved_preview["secondary_kpi"]
    preview_secondary_goal = saved_preview["secondary_goal"]
    preview_roas = saved_preview["roas_goal"]

    with st.expander("Campaign KPI Setup — Goals Applied", expanded=False):
        summary_text = (
            f"**Primary:** {preview_primary} = {preview_primary_goal:g}  \n"
        )
        if preview_secondary:
            summary_text += (
                f"**Secondary:** {preview_secondary} = "
                f"{preview_secondary_goal:g}  \n"
            )
        else:
            summary_text += "**Secondary:** None  \n"

        summary_text += f"**ROAS Target:** {preview_roas:g}x"
        st.markdown(summary_text)

        if st.button(
            "Edit KPI Goals",
            use_container_width=True,
            key=f"edit_kpi_goals_{campaign_key}"
        ):
            del st.session_state[config_state_key]
            st.rerun()

else:
    st.markdown(
        '<div class="section-label">Campaign KPI Setup</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Choose the campaign's primary and secondary KPIs and enter their targets. "
        "Detected report KPIs are used only as defaults—you can always override them. "
        "ROAS is tracked separately for every campaign."
    )

    primary_widget_key = f"main_primary_kpi_{campaign_key}"
    secondary_widget_key = f"main_secondary_kpi_{campaign_key}"

    if primary_widget_key not in st.session_state:
        st.session_state[primary_widget_key] = (
            detected_primary_kpi
            if detected_primary_kpi in KPI_OPTIONS
            else "CPA"
        )

    if st.session_state.get(primary_widget_key) not in KPI_OPTIONS:
        st.session_state[primary_widget_key] = "CPA"

    setup_col1, setup_col2 = st.columns(2, gap="large")

    with setup_col1:
        st.markdown("#### Primary KPI")

        primary_kpi = st.selectbox(
            "Primary KPI",
            KPI_OPTIONS,
            key=primary_widget_key,
            help=(
                f"Report suggestion: {detected_primary_kpi}. You can override it."
                if detected_primary_kpi
                else "Select the campaign's primary KPI."
            )
        )

        primary_kpi_goal = st.number_input(
            f"{primary_kpi} Target",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            placeholder="Enter target",
            help=kpi_goal_help(primary_kpi),
            key=f"main_primary_goal_{campaign_key}_{primary_kpi}"
        )

    with setup_col2:
        st.markdown("#### Secondary KPI")

        secondary_options = ["None"] + KPI_OPTIONS

        if secondary_widget_key not in st.session_state:
            st.session_state[secondary_widget_key] = (
                detected_secondary_kpi
                if detected_secondary_kpi in KPI_OPTIONS
                else "None"
            )

        if st.session_state.get(secondary_widget_key) not in secondary_options:
            st.session_state[secondary_widget_key] = "None"

        secondary_kpi_choice = st.selectbox(
            "Secondary KPI",
            secondary_options,
            key=secondary_widget_key,
            help=(
                f"Report suggestion: {detected_secondary_kpi}. You can override it."
                if detected_secondary_kpi
                else "Optional supporting KPI."
            )
        )

        secondary_kpi = (
            None if secondary_kpi_choice == "None"
            else secondary_kpi_choice
        )

        secondary_kpi_goal = None
        if secondary_kpi:
            secondary_kpi_goal = st.number_input(
                f"{secondary_kpi} Target",
                min_value=0.0,
                value=None,
                step=0.01,
                format="%.2f",
                placeholder="Enter target",
                help=kpi_goal_help(secondary_kpi),
                key=f"main_secondary_goal_{campaign_key}_{secondary_kpi}"
            )
        else:
            st.info("No secondary KPI selected.")

    st.markdown("#### ROAS Goal")
    st.caption(
        "ROAS is tracked independently for every campaign and is not part of the "
        "Primary or Secondary KPI dropdowns."
    )

    roas_target_input = st.number_input(
        "ROAS Target",
        min_value=0.0,
        value=None,
        step=0.10,
        format="%.2f",
        placeholder="Enter ROAS target (for example 3.0)",
        help="Minimum required return on ad spend. Example: 3.0 means 3x.",
        key=f"main_roas_goal_{campaign_key}"
    )

    apply_goals = st.button(
        "Apply KPI Goals & Analyze",
        type="primary",
        use_container_width=True,
        key=f"apply_kpi_goals_{campaign_key}"
    )

    if apply_goals:
        if primary_kpi_goal is None:
            st.error("Enter a target for the Primary KPI.")
            st.stop()

        if secondary_kpi and secondary_kpi == primary_kpi:
            st.error(
                "Primary and Secondary KPI cannot be the same. "
                "Choose a different Secondary KPI or select None."
            )
            st.stop()

        if secondary_kpi and secondary_kpi_goal is None:
            st.error("Enter a target for the Secondary KPI.")
            st.stop()

        if roas_target_input is None:
            st.error("Enter the campaign ROAS target.")
            st.stop()

        st.session_state[config_state_key] = {
            "primary_kpi": primary_kpi,
            "primary_goal": float(primary_kpi_goal),
            "secondary_kpi": secondary_kpi,
            "secondary_goal": (
                float(secondary_kpi_goal)
                if secondary_kpi else None
            ),
            "roas_goal": float(roas_target_input)
        }
        st.rerun()

    st.info(
        "Set the campaign KPI target(s) above and click "
        "'Apply KPI Goals & Analyze' to load the analysis."
    )
    st.stop()

saved_config = st.session_state[config_state_key]
primary_kpi = saved_config["primary_kpi"]
primary_kpi_goal = saved_config["primary_goal"]
secondary_kpi = saved_config["secondary_kpi"]
secondary_kpi_goal = saved_config["secondary_goal"]
roas_goal = saved_config["roas_goal"]

campaign_kpi_goals = {
    primary_kpi: float(primary_kpi_goal),
    "ROAS": float(roas_goal)
}
if secondary_kpi:
    campaign_kpi_goals[secondary_kpi] = float(secondary_kpi_goal)

if reported_funnel_stage != "Not Assigned":
    funnel_stage = reported_funnel_stage
else:
    funnel_stage = infer_funnel_from_kpis(
        primary_kpi,
        secondary_kpi
    )

goal_summary = (
    f"Primary: {primary_kpi} = {primary_kpi_goal:g}"
)
if secondary_kpi:
    goal_summary += (
        f"  •  Secondary: {secondary_kpi} = {secondary_kpi_goal:g}"
    )
goal_summary += f"  •  ROAS = {roas_goal:g}"

st.success(f"Campaign goals applied — {goal_summary}")

# ---------------------------------------------------
# END SECTION 5
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 6: CALCULATE CAMPAIGN DATE RANGE
# ---------------------------------------------------

campaign_start = campaign_df["Date"].min()
campaign_end = campaign_df["Date"].max()

if pd.notna(campaign_start) and pd.notna(campaign_end):
    date_range_text = (
        f"{campaign_start.strftime('%b %Y')} – "
        f"{campaign_end.strftime('%b %Y')}"
    )
else:
    date_range_text = "Date range unavailable"

# ---------------------------------------------------
# END SECTION 6
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 7: CALCULATE BASIC CAMPAIGN METRICS
# ---------------------------------------------------

spend = campaign_df["Spend_USD"].sum()
impressions = campaign_df["Impressions_Served"].sum()
clicks = campaign_df["Clicks"].sum()

# ---------------------------------------------------
# END SECTION 7
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 8: CALCULATE CPM AND CTR
# ---------------------------------------------------

if impressions > 0:
    cpm = (spend / impressions) * 1000
    ctr = (clicks / impressions) * 100
else:
    cpm = 0
    ctr = 0

# ---------------------------------------------------
# END SECTION 8
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 9: CALCULATE CONVERSIONS
# ---------------------------------------------------

view_conversions = campaign_df["Conv_View_Through"].sum()
click_conversions = campaign_df["Conv_Click_Through"].sum()

total_conversions = (
    view_conversions
    + click_conversions
)

# ---------------------------------------------------
# END SECTION 9
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 10: CALCULATE CPA
# ---------------------------------------------------

if total_conversions > 0:
    cpa = spend / total_conversions
else:
    cpa = 0

# ---------------------------------------------------
# END SECTION 10
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 11: CALCULATE CPC AND CONVERSION RATE
# ---------------------------------------------------

if clicks > 0:
    cpc = spend / clicks
    conversion_rate = (
        click_conversions / clicks
    ) * 100
else:
    cpc = 0
    conversion_rate = 0

# ---------------------------------------------------
# END SECTION 11
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 12: CALCULATE REVENUE AND ROAS
# ---------------------------------------------------

revenue = campaign_df[
    "Revenue_Attributed_USD"
].sum()

if spend > 0:
    roas = revenue / spend
else:
    roas = 0

# ---------------------------------------------------
# END SECTION 12
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 13: CALCULATE COMPLETION RATE AND VIEWABILITY
# ---------------------------------------------------
# Completion Rate is currently a simple average of the
# row-level values in the report.
#
# Campaign Viewability is calculated from raw totals and is
# used as the Awareness comparison baseline in the audience
# recommendation engine.

if "Completion_Rate_%" in campaign_df.columns:
    completion_rate = campaign_df[
        "Completion_Rate_%"
    ].mean()
else:
    completion_rate = 0


viewable_impressions = campaign_df[
    "Impressions_Viewable"
].sum()

if impressions > 0:
    campaign_viewability = (
        viewable_impressions
        / impressions
    ) * 100
else:
    campaign_viewability = 0

# ---------------------------------------------------
# END SECTION 13
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 14: CALCULATE CAMPAIGN BUDGET
# ---------------------------------------------------
# The line-item budget repeats across rows, so we keep only
# unique Line Item + Budget combinations before summing.

unique_line_item_budgets = campaign_df[
    [
        "Line_Item_Name",
        "Flight_Budget_USD"
    ]
].drop_duplicates()

budget = unique_line_item_budgets[
    "Flight_Budget_USD"
].sum()

# ---------------------------------------------------
# END SECTION 14
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 15: CALCULATE BUDGET DELIVERY
# ---------------------------------------------------

if budget > 0:
    delivery_percent = (
        spend / budget
    ) * 100
else:
    delivery_percent = 0

# ---------------------------------------------------
# END SECTION 15
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 16: DEFINE CAMPAIGN-SPECIFIC KPI TARGETS
# ---------------------------------------------------
# Targets now come from the user's Campaign KPI Goals configuration.
# For a legacy analyzer metric that is not one of the campaign's selected KPIs,
# use the campaign's current value as a neutral comparison baseline instead of
# inventing a hard-coded target.

cpa_target = campaign_kpi_goals.get("CPA", cpa if cpa > 0 else float("inf"))
roas_target = campaign_kpi_goals.get("ROAS", roas if roas > 0 else 0.0)
completion_rate_target = campaign_kpi_goals.get(
    "Completion Rate",
    completion_rate if completion_rate > 0 else 0.0
)

viewability_target = campaign_kpi_goals.get(
    "Viewability",
    campaign_viewability if campaign_viewability > 0 else 0.0
)
ctr_target = campaign_kpi_goals.get("CTR", ctr if ctr > 0 else 0.0)
cpm_target = campaign_kpi_goals.get("CPM", cpm if cpm > 0 else float("inf"))
cpc_target = campaign_kpi_goals.get("CPC", cpc if cpc > 0 else float("inf"))
conversion_rate_target = campaign_kpi_goals.get(
    "Conversion Rate",
    conversion_rate if conversion_rate > 0 else 0.0
)

# ---------------------------------------------------
# END SECTION 16
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 17: DETERMINE KPI STATUS
# ---------------------------------------------------

if 95 <= delivery_percent <= 105:
    delivery_status = "On Track"

elif delivery_percent < 95:
    delivery_status = "Under-Delivering"

else:
    delivery_status = "Over-Delivering"


if cpa <= cpa_target:
    cpa_status = "Efficient"
else:
    cpa_status = "Above Target"


if roas >= roas_target:
    roas_status = "Strong"
else:
    roas_status = "Below Target"


if completion_rate >= completion_rate_target:
    completion_rate_status = "Strong"
else:
    completion_rate_status = "Below Target"

# ---------------------------------------------------
# END SECTION 17
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 18: HELPER FUNCTIONS FOR DASHBOARD TILES
# ---------------------------------------------------
# These reusable functions create responsive HTML cards.
#
# IMPORTANT:
# The HTML is intentionally generated without leading indentation.
# Markdown treats HTML lines that begin with four spaces as code,
# which was the reason the previous version displayed raw </div>
# tags on the dashboard.

def build_tile_html(label, value, note=None):
    """
    Return one compact HTML KPI tile with no leading indentation.
    """

    note_html = (
        f'<div class="tile-note">{note}</div>'
        if note
        else ""
    )

    return (
        '<div class="tile">'
        f'<div class="tile-label">{label}</div>'
        f'<div class="tile-value">{value}</div>'
        f'{note_html}'
        '</div>'
    )


def render_tile_grid(tiles, compact=False):
    """
    Render a responsive grid of KPI tiles.

    CSS auto-fit/minmax allows the tiles to resize and wrap
    automatically based on the available browser width.
    """

    grid_class = (
        "tile-grid-compact"
        if compact
        else "tile-grid"
    )

    tile_html = "".join(
        build_tile_html(
            tile["label"],
            tile["value"],
            tile.get("note")
        )
        for tile in tiles
    )

    full_html = (
        f'<div class="{grid_class}">'
        f'{tile_html}'
        '</div>'
    )

    st.markdown(
        full_html,
        unsafe_allow_html=True
    )


def render_health_card(
    label,
    status_text,
    state="good"
):
    """
    Render one compact health card.

    state:
    - good
    - warn
    - bad
    """

    if state == "good":
        css_class = "status-good"
        icon = "✅"

    elif state == "bad":
        css_class = "status-bad"
        icon = "🔴"

    else:
        css_class = "status-warn"
        icon = "⚠️"

    health_html = (
        '<div class="health-card">'
        f'<div class="health-label">{label}</div>'
        f'<div class="health-value {css_class}">'
        f'{icon} {status_text}'
        '</div>'
        '</div>'
    )

    st.markdown(
        health_html,
        unsafe_allow_html=True
    )


def format_compact_number(value, decimals=2):
    """Format large numeric values using K / M / B."""
    if pd.isna(value):
        return "N/A"

    value = float(value)
    absolute_value = abs(value)

    if absolute_value >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:.{decimals}f}".rstrip("0").rstrip(".")
        return f"{formatted}B"
    if absolute_value >= 1_000_000:
        formatted = f"{value / 1_000_000:.{decimals}f}".rstrip("0").rstrip(".")
        return f"{formatted}M"
    if absolute_value >= 1_000:
        formatted = f"{value / 1_000:.{decimals}f}".rstrip("0").rstrip(".")
        return f"{formatted}K"

    if float(value).is_integer():
        return f"{value:,.0f}"

    return f"{value:,.{decimals}f}".rstrip("0").rstrip(".")


def format_currency(value):
    """Standard money format: $ plus compact K / M / B for large values."""
    if pd.isna(value):
        return "N/A"

    value = float(value)
    if abs(value) >= 1_000:
        return f"${format_compact_number(value)}"
    return f"${value:,.2f}"


def format_percent(value):
    """Standard rate format."""
    if pd.isna(value):
        return "N/A"
    return f"{float(value):.2f}%"


def format_multiplier(value):
    """Standard ROAS / index format."""
    if pd.isna(value) or not np.isfinite(value):
        return "N/A"
    return f"{float(value):.2f}x"


def format_metric_value(metric_name, value):
    """One formatting standard used across the entire dashboard."""
    if pd.isna(value):
        return "N/A"

    currency_metrics = {
        "Spend", "Budget", "CPM", "CPC", "CPA", "Revenue",
        "Attributed Revenue", "Flight_Budget_USD", "Spend_USD",
        "Revenue_Attributed_USD"
    }
    percent_metrics = {
        "CTR", "Conversion Rate", "Completion Rate", "Viewability",
        "Spend Share", "Conversion Share", "Revenue Share", "Impression Share",
        "Budget Delivery", "Delivery"
    }
    multiplier_metrics = {
        "ROAS", "Efficiency Index", "CPA Index", "ROAS Index",
        "Completion Index", "Viewability Index", "CPM Efficiency"
    }

    if metric_name in currency_metrics:
        return format_currency(value)
    if metric_name in percent_metrics:
        return format_percent(value)
    if metric_name in multiplier_metrics or "Index" in str(metric_name):
        return format_multiplier(value)

    return format_compact_number(value)


def format_dataframe_for_display(dataframe):
    """Apply dashboard formatting without changing calculation data."""
    display_df = dataframe.copy()

    for column in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[column]):
            display_df[column] = display_df[column].apply(
                lambda value, metric=column: format_metric_value(metric, value)
            )

    return display_df


def format_monthly_metric_value(metric_name, value):
    return format_metric_value(metric_name, value)



# ---------------------------------------------------
# DETAILED ANALYSIS HELPERS
# ---------------------------------------------------
# These functions power Audience, Creative, Inventory,
# and Domain / Website analysis.
#
# The same funnel-stage logic is reused everywhere:
#
# Awareness campaigns prioritize:
# - Spend
# - Impressions
# - CPM
# - Completion Rate
# - Viewability
# - CTR / CPC as supporting engagement metrics
#
# Conversion campaigns prioritize:
# - Spend
# - Conversions
# - CPA
# - Revenue
# - ROAS
# - Conversion Rate
# - CTR / CPC as supporting media metrics


def safe_divide(numerator, denominator, multiplier=1):
    """
    Safely divide two numeric values or pandas Series.
    Returns NaN where the denominator is zero.
    """

    return np.where(
        denominator != 0,
        (numerator / denominator) * multiplier,
        np.nan
    )


def weighted_average(values, weights):
    """
    Calculate a weighted average while ignoring missing values.
    Returns NaN when no valid weighted observations exist.
    """

    valid = (
        values.notna()
        & weights.notna()
        & (weights > 0)
    )

    if valid.sum() == 0:
        return np.nan

    return np.average(
        values[valid],
        weights=weights[valid]
    )


def aggregate_dimension_performance(
    data,
    dimension_column,
    metadata_columns=None
):
    """
    Aggregate campaign performance by one analysis dimension.

    Examples:
    - Audience_Segment
    - Creative_Name
    - Channel
    - Deal_Type
    - Device_Type
    - Publisher

    Rates are recalculated from raw totals wherever possible.
    Completion Rate is currently impression-weighted because
    the source report provides a row-level rate but not video
    completion counts.
    """

    metadata_columns = metadata_columns or []

    working = data.copy()

    working = working[
        working[dimension_column].notna()
    ].copy()

    if working.empty:
        return pd.DataFrame()


    # ---------------------------------------------------
    # Impression-weighted completion contribution
    # ---------------------------------------------------

    working["_completion_weighted"] = (
        working["Completion_Rate_%"].fillna(0)
        * working["Impressions_Served"].fillna(0)
    )


    # ---------------------------------------------------
    # Additive metrics
    # ---------------------------------------------------

    grouped = (
        working
        .groupby(
            dimension_column,
            as_index=False
        )
        .agg(
            Spend=("Spend_USD", "sum"),
            Impressions=("Impressions_Served", "sum"),
            Viewable_Impressions=("Impressions_Viewable", "sum"),
            Clicks=("Clicks", "sum"),
            View_Through_Conversions=("Conv_View_Through", "sum"),
            Click_Through_Conversions=("Conv_Click_Through", "sum"),
            Revenue=("Revenue_Attributed_USD", "sum"),
            Completion_Weighted=("_completion_weighted", "sum"),
            Active_Days=("Date", "nunique"),
            Data_Quality_Warnings=(
                "Data_Quality_Status",
                lambda values: int((values.astype(str) == "Warning").sum())
            )
        )
    )


    grouped["Total Conversions"] = (
        grouped["View_Through_Conversions"]
        + grouped["Click_Through_Conversions"]
    )


    # ---------------------------------------------------
    # Recalculate derived KPIs from aggregated totals
    # ---------------------------------------------------

    grouped["CPM"] = safe_divide(
        grouped["Spend"],
        grouped["Impressions"],
        1000
    )

    grouped["CTR"] = safe_divide(
        grouped["Clicks"],
        grouped["Impressions"],
        100
    )

    grouped["CPC"] = safe_divide(
        grouped["Spend"],
        grouped["Clicks"]
    )

    grouped["CPA"] = safe_divide(
        grouped["Spend"],
        grouped["Total Conversions"]
    )

    grouped["Conversion Rate"] = safe_divide(
        grouped["Click_Through_Conversions"],
        grouped["Clicks"],
        100
    )

    grouped["ROAS"] = safe_divide(
        grouped["Revenue"],
        grouped["Spend"]
    )

    grouped["Viewability"] = safe_divide(
        grouped["Viewable_Impressions"],
        grouped["Impressions"],
        100
    )

    grouped["Completion Rate"] = safe_divide(
        grouped["Completion_Weighted"],
        grouped["Impressions"]
    )


    # ---------------------------------------------------
    # Add metadata such as Creative Length
    # ---------------------------------------------------

    for metadata_column in metadata_columns:

        metadata = (
            working
            .groupby(dimension_column)[metadata_column]
            .first()
            .reset_index()
        )

        grouped = grouped.merge(
            metadata,
            on=dimension_column,
            how="left"
        )


    # ---------------------------------------------------
    # Assign a simple investigation status based on funnel
    # stage and campaign target logic.
    # ---------------------------------------------------

    if funnel_stage == "Awareness":

        grouped["Status"] = np.where(
            grouped["Completion Rate"] >= completion_rate_target,
            "Strong",
            np.where(
                grouped["Completion Rate"] >= (
                    completion_rate_target - 5
                ),
                "Watch",
                "Needs Attention"
            )
        )


    elif funnel_stage == "Conversion":

        cpa_meets = (
            grouped["CPA"].notna()
            & (grouped["CPA"] <= cpa_target)
        )

        roas_meets = (
            grouped["ROAS"].notna()
            & (grouped["ROAS"] >= roas_target)
        )

        grouped["Status"] = np.select(
            [
                cpa_meets & roas_meets,
                cpa_meets | roas_meets
            ],
            [
                "Strong",
                "Watch"
            ],
            default="Needs Attention"
        )


    else:

        grouped["Status"] = "Not Evaluated"


    return grouped




# ---------------------------------------------------
# DECISION SUPPORT: EVIDENCE, GUARDRAILS, EXPLAINABILITY
# ---------------------------------------------------
# TradeIQ does not treat an index crossing a threshold as sufficient evidence
# for a high-risk optimization. Every recommendation is enriched with:
#   1) Evidence Strength / minimum-volume rules
#   2) Primary + Secondary KPI + ROAS guardrails
#   3) Signal -> Interpretation -> Action -> Risk reasoning
# These fields are shared by all analyzers and the Optimization Action Center.

LOWER_IS_BETTER_KPIS = {"CPA", "CPM", "CPC"}


def evaluate_kpi_guardrail(metric_name, actual_value, goal_value):
    """Return PASS / CONDITIONAL / FAIL / NOT AVAILABLE for one KPI goal."""
    if metric_name is None or goal_value is None:
        return "NOT REQUIRED"

    if actual_value is None or pd.isna(actual_value) or not np.isfinite(float(actual_value)):
        return "NOT AVAILABLE"

    actual_value = float(actual_value)
    goal_value = float(goal_value)

    if metric_name in LOWER_IS_BETTER_KPIS:
        if actual_value <= goal_value:
            return "PASS"
        if actual_value <= goal_value * 1.10:
            return "CONDITIONAL"
        return "FAIL"

    if actual_value >= goal_value:
        return "PASS"
    if actual_value >= goal_value * 0.90:
        return "CONDITIONAL"
    return "FAIL"


def compute_evidence_strength(row):
    """
    Conservative minimum-evidence rules.

    This is intentionally called Evidence Strength rather than statistical
    confidence because the rule is based on observed volume, allocation, and
    time in market—not a formal confidence interval.
    """
    spend_share = float(row.get("Spend Share", 0) or 0)
    active_days = int(row.get("Active_Days", 0) or 0)

    if funnel_stage == "Conversion":
        volume = float(row.get("Total Conversions", 0) or 0)
        if spend_share >= 5 and volume >= 50 and active_days >= 7:
            return "Strong"
        if spend_share >= 2 and volume >= 20 and active_days >= 3:
            return "Moderate"
        return "Weak"

    if funnel_stage == "Awareness":
        volume = float(row.get("Impressions", 0) or 0)
        if spend_share >= 5 and volume >= 2_000_000 and active_days >= 7:
            return "Strong"
        if spend_share >= 2 and volume >= 500_000 and active_days >= 3:
            return "Moderate"
        return "Weak"

    return "Weak"


def _format_goal_check(metric_name, actual, goal, status):
    if metric_name is None:
        return "Not required"
    actual_text = format_metric_value(metric_name, actual) if pd.notna(actual) else "N/A"
    goal_text = format_metric_value(metric_name, goal) if goal is not None else "N/A"
    return f"{metric_name}: {actual_text} vs goal {goal_text} ({status})"


def apply_decision_support(result_df, analyzer_type):
    """Apply TradeIQ's common evidence and guardrail framework to an analyzer."""
    if result_df is None or result_df.empty:
        return result_df

    result = result_df.copy()

    evidence_strengths = []
    primary_checks = []
    secondary_checks = []
    roas_checks = []
    guardrail_statuses = []
    final_recommendations = []
    signals = []
    interpretations = []
    actions = []
    risks = []
    rationales = []

    positive_actions = {"SCALE", "PRIORITIZE", "PROMISING - GATHER MORE DATA"}
    severe_negative_actions = {"NEGATION CANDIDATE", "PAUSE CANDIDATE", "AVOID / REDUCE"}
    reduce_actions = {"REDUCE", "REFRESH / REDUCE"}

    for _, row in result.iterrows():
        evidence = compute_evidence_strength(row)

        primary_actual = row.get(primary_kpi, np.nan)
        primary_check = evaluate_kpi_guardrail(
            primary_kpi, primary_actual, primary_kpi_goal
        )

        if secondary_kpi:
            secondary_actual = row.get(secondary_kpi, np.nan)
            secondary_check = evaluate_kpi_guardrail(
                secondary_kpi, secondary_actual, secondary_kpi_goal
            )
        else:
            secondary_actual = np.nan
            secondary_check = "NOT REQUIRED"

        roas_actual = row.get("ROAS", np.nan)
        roas_check = evaluate_kpi_guardrail("ROAS", roas_actual, roas_goal)

        required_checks = [primary_check, roas_check]
        if secondary_kpi:
            required_checks.append(secondary_check)

        if "FAIL" in required_checks:
            guardrail_status = "Failed"
        elif "NOT AVAILABLE" in required_checks:
            guardrail_status = "Incomplete"
        elif "CONDITIONAL" in required_checks:
            guardrail_status = "Conditional"
        else:
            guardrail_status = "Passed"

        original_recommendation = str(row.get("Recommendation", "WATCH")).strip()
        final_recommendation = original_recommendation

        # Positive optimization requires evidence + KPI protection.
        if original_recommendation in positive_actions:
            if evidence == "Weak":
                final_recommendation = "GATHER MORE DATA"
            elif guardrail_status in {"Failed", "Incomplete"}:
                final_recommendation = "DO NOT SCALE - GUARDRAIL FAILED"
            elif evidence == "Moderate" or guardrail_status == "Conditional":
                final_recommendation = "CONTROLLED TEST"
            elif original_recommendation == "PROMISING - GATHER MORE DATA":
                final_recommendation = "PRIORITIZE"

        # High-risk negative actions also require strong evidence.
        elif original_recommendation in severe_negative_actions:
            if evidence == "Weak":
                final_recommendation = "INVESTIGATE - MORE DATA NEEDED"
            elif evidence == "Moderate":
                final_recommendation = "REDUCE / INVESTIGATE"

        elif original_recommendation in reduce_actions and evidence == "Weak":
            final_recommendation = "INVESTIGATE - MORE DATA NEEDED"

        # ---------------- Structured reason text ----------------
        spend_share = row.get("Spend Share", np.nan)
        warnings = int(row.get("Data_Quality_Warnings", 0) or 0)
        active_days = int(row.get("Active_Days", 0) or 0)

        if funnel_stage == "Conversion":
            conv_share = row.get("Conversion Share", np.nan)
            efficiency = row.get("Efficiency Index", np.nan)
            cpa_value = row.get("CPA", np.nan)
            roas_value = row.get("ROAS", np.nan)

            signal = (
                f"{format_percent(conv_share) if pd.notna(conv_share) else 'N/A'} of conversions "
                f"from {format_percent(spend_share) if pd.notna(spend_share) else 'N/A'} of spend; "
                f"CPA {format_currency(cpa_value) if pd.notna(cpa_value) else 'N/A'} and "
                f"ROAS {format_multiplier(roas_value) if pd.notna(roas_value) else 'N/A'}."
            )
            interpretation = (
                f"Efficiency Index {format_multiplier(efficiency) if pd.notna(efficiency) else 'N/A'}. "
                f"Primary guardrail: {_format_goal_check(primary_kpi, primary_actual, primary_kpi_goal, primary_check)}. "
                f"ROAS guardrail: {_format_goal_check('ROAS', roas_actual, roas_goal, roas_check)}."
            )
        else:
            impression_share = row.get("Impression Share", np.nan)
            completion_index = row.get("Completion Index", np.nan)
            signal = (
                f"{format_percent(impression_share) if pd.notna(impression_share) else 'N/A'} of impressions "
                f"from {format_percent(spend_share) if pd.notna(spend_share) else 'N/A'} of spend; "
                f"Completion Index {format_multiplier(completion_index) if pd.notna(completion_index) else 'N/A'}."
            )
            interpretation = (
                f"Primary guardrail: {_format_goal_check(primary_kpi, primary_actual, primary_kpi_goal, primary_check)}. "
                f"ROAS guardrail: {_format_goal_check('ROAS', roas_actual, roas_goal, roas_check)}."
            )

        if secondary_kpi:
            interpretation += " " + _format_goal_check(
                secondary_kpi, secondary_actual, secondary_kpi_goal, secondary_check
            ) + "."

        action_map = {
            "SCALE": "Consider a measured increase in allocation while monitoring the configured KPI guardrails.",
            "PRIORITIZE": "Prioritize this entity for incremental budget before weaker alternatives.",
            "CONTROLLED TEST": "Use a small, controlled allocation change and re-evaluate after sufficient new data accumulates.",
            "DO NOT SCALE - GUARDRAIL FAILED": "Do not add exposure yet. Diagnose the failed KPI guardrail before considering scale.",
            "GATHER MORE DATA": "Hold the current setup and gather more observations before making a material optimization.",
            "NEGATION CANDIDATE": "Validate business/context constraints, then consider exclusion or material reduction.",
            "PAUSE CANDIDATE": "Validate the signal, then consider pausing or replacing the creative.",
            "AVOID / REDUCE": "Reduce exposure after confirming the underperformance is not caused by a reporting anomaly.",
            "REDUCE": "Reduce exposure in a controlled way and monitor whether the primary KPI improves.",
            "REFRESH / REDUCE": "Reduce rotation and consider a creative refresh before a full pause.",
            "REDUCE / INVESTIGATE": "Investigate the driver and use a partial reduction rather than an immediate hard stop.",
            "INVESTIGATE - MORE DATA NEEDED": "Investigate the signal but avoid a high-impact change until evidence becomes stronger.",
            "INVESTIGATE": "Diagnose the underlying driver before changing allocation.",
            "MAINTAIN": "Maintain the current setup; no material optimization is supported by the evidence.",
            "WATCH": "Continue monitoring. Current signals are mixed and do not justify a material change.",
            "INSUFFICIENT DATA": "Gather more data before taking action."
        }
        action_text = action_map.get(
            final_recommendation,
            "Review the evidence and use trader judgment before changing the DSP."
        )

        risk_parts = [
            f"Evidence Strength is {evidence} based on volume, spend share, and {active_days} active day(s)."
        ]
        if guardrail_status != "Passed":
            risk_parts.append(f"Guardrail status is {guardrail_status}.")
        if warnings > 0:
            risk_parts.append(f"{warnings} source row warning(s) are present for this entity and should be reviewed.")
        if final_recommendation in {"SCALE", "PRIORITIZE", "CONTROLLED TEST"}:
            risk_parts.append("Performance may deteriorate as spend expands; re-check CPA/ROAS and the secondary KPI after the change.")
        risk_text = " ".join(risk_parts)

        rationale = (
            f"SIGNAL: {signal} | INTERPRETATION: {interpretation} | "
            f"ACTION: {action_text} | RISK: {risk_text}"
        )

        evidence_strengths.append(evidence)
        primary_checks.append(primary_check)
        secondary_checks.append(secondary_check)
        roas_checks.append(roas_check)
        guardrail_statuses.append(guardrail_status)
        final_recommendations.append(final_recommendation)
        signals.append(signal)
        interpretations.append(interpretation)
        actions.append(action_text)
        risks.append(risk_text)
        rationales.append(rationale)

    result["Original Recommendation"] = result["Recommendation"]
    result["Recommendation"] = final_recommendations
    result["Evidence Strength"] = evidence_strengths
    # Keep the existing column for backwards-compatible UI, but make the label
    # truthful by using evidence strength rather than statistical confidence.
    result["Confidence"] = evidence_strengths
    result["Primary Guardrail"] = primary_checks
    result["Secondary Guardrail"] = secondary_checks
    result["ROAS Guardrail"] = roas_checks
    result["Guardrail Status"] = guardrail_statuses
    result["Signal"] = signals
    result["Interpretation"] = interpretations
    result["Action Guidance"] = actions
    result["Risk"] = risks
    result["Reason"] = rationales

    return result


def calculate_audience_recommendations(data):
    """
    Build a decision-focused audience scorecard.

    Only indices that directly influence an optimization
    decision are retained.

    CONVERSION
    ----------
    - Spend Share
    - Conversion Share
    - Revenue Share
    - Efficiency Index = Conversion Share / Spend Share
    - CPA Index = Campaign CPA / Audience CPA
    - ROAS Index = Audience ROAS / Campaign ROAS
    - Confidence

    AWARENESS
    ---------
    - Spend Share
    - Impression Share
    - Completion Index =
        Audience Completion Rate / Campaign Completion Rate
    - CPM Efficiency =
        Campaign CPM / Audience CPM
    - Confidence

    CTR and Viewability remain diagnostic context only.
    """

    audience_df = aggregate_dimension_performance(
        data,
        "Audience_Segment"
    )

    if audience_df.empty:
        return audience_df

    total_spend = audience_df["Spend"].sum()

    audience_df["Spend Share"] = safe_divide(
        audience_df["Spend"],
        total_spend,
        100
    )

    # ---------------------------------------------------
    # CONVERSION FUNNEL
    # ---------------------------------------------------
    if funnel_stage == "Conversion":

        total_conversions = audience_df["Total Conversions"].sum()
        total_revenue = audience_df["Revenue"].sum()

        audience_df["Conversion Share"] = safe_divide(
            audience_df["Total Conversions"],
            total_conversions,
            100
        )

        audience_df["Revenue Share"] = safe_divide(
            audience_df["Revenue"],
            total_revenue,
            100
        )

        audience_df["Efficiency Index"] = safe_divide(
            audience_df["Conversion Share"],
            audience_df["Spend Share"]
        )

        audience_df["CPA Index"] = safe_divide(
            cpa,
            audience_df["CPA"]
        )

        audience_df["ROAS Index"] = safe_divide(
            audience_df["ROAS"],
            roas
        )

        audience_df["Confidence"] = np.select(
            [
                (
                    (audience_df["Spend Share"] >= 5)
                    & (audience_df["Total Conversions"] >= 30)
                ),
                (
                    (audience_df["Spend Share"] >= 2)
                    & (audience_df["Total Conversions"] >= 10)
                )
            ],
            ["High", "Medium"],
            default="Low"
        )

        recommendations = []
        reasons = []

        for _, row in audience_df.iterrows():

            spend_share = row["Spend Share"]
            conversions = row["Total Conversions"]
            conversion_share = row["Conversion Share"]
            revenue_share = row["Revenue Share"]
            efficiency = row["Efficiency Index"]
            cpa_index = row["CPA Index"]
            roas_index = row["ROAS Index"]
            confidence = row["Confidence"]

            if confidence == "Low":

                if (
                    pd.notna(efficiency)
                    and efficiency >= 1.20
                    and (
                        cpa_index >= 1.00
                        or roas_index >= 1.00
                    )
                    and conversions > 0
                ):
                    recommendation = "PROMISING - GATHER MORE DATA"
                    reason = (
                        f"{conversion_share:.1f}% conversion share on "
                        f"{spend_share:.1f}% spend share "
                        f"(Efficiency Index {efficiency:.2f}), but "
                        f"confidence is low."
                    )
                else:
                    recommendation = "INSUFFICIENT DATA"
                    reason = (
                        f"Spend Share is {spend_share:.1f}% with "
                        f"{conversions:,.0f} conversions. More data is "
                        f"needed before taking action."
                    )

            elif (
                confidence == "High"
                and efficiency < 0.40
                and cpa_index < 0.75
                and roas_index < 0.75
            ):
                recommendation = "NEGATION CANDIDATE"
                reason = (
                    f"Only {conversion_share:.1f}% of conversions on "
                    f"{spend_share:.1f}% of spend. Efficiency Index "
                    f"{efficiency:.2f}, CPA Index {cpa_index:.2f}, "
                    f"ROAS Index {roas_index:.2f}. Validate before exclusion."
                )

            elif (
                confidence == "High"
                and efficiency >= 1.20
                and cpa_index >= 1.10
                and roas_index >= 1.10
            ):
                recommendation = "SCALE"
                reason = (
                    f"{conversion_share:.1f}% conversion share and "
                    f"{revenue_share:.1f}% revenue share on "
                    f"{spend_share:.1f}% spend share. Efficiency Index "
                    f"{efficiency:.2f}, CPA Index {cpa_index:.2f}, "
                    f"ROAS Index {roas_index:.2f}."
                )

            elif (
                efficiency >= 1.10
                and (
                    cpa_index >= 1.00
                    or roas_index >= 1.00
                )
            ):
                recommendation = "PRIORITIZE"
                reason = (
                    f"Conversion contribution exceeds spend allocation: "
                    f"{conversion_share:.1f}% vs {spend_share:.1f}% "
                    f"(Efficiency Index {efficiency:.2f})."
                )

            elif (
                efficiency < 0.75
                and cpa_index < 0.90
                and roas_index < 0.90
            ):
                recommendation = "REDUCE"
                reason = (
                    f"Efficiency Index {efficiency:.2f}, CPA Index "
                    f"{cpa_index:.2f}, and ROAS Index {roas_index:.2f} "
                    f"all indicate underperformance."
                )

            elif (
                0.90 <= efficiency <= 1.10
                and 0.90 <= cpa_index <= 1.10
                and 0.90 <= roas_index <= 1.10
            ):
                recommendation = "MAINTAIN"
                reason = (
                    f"All decision indices are close to campaign average: "
                    f"Efficiency {efficiency:.2f}, CPA {cpa_index:.2f}, "
                    f"ROAS {roas_index:.2f}."
                )

            elif efficiency < 0.90:
                recommendation = "INVESTIGATE"
                reason = (
                    f"Conversion Share ({conversion_share:.1f}%) trails "
                    f"Spend Share ({spend_share:.1f}%). Review before reducing."
                )

            else:
                recommendation = "WATCH"
                reason = (
                    f"Mixed signals: Efficiency Index {efficiency:.2f}, "
                    f"CPA Index {cpa_index:.2f}, ROAS Index {roas_index:.2f}."
                )

            recommendations.append(recommendation)
            reasons.append(reason)

        audience_df["Recommendation"] = recommendations
        audience_df["Reason"] = reasons

    # ---------------------------------------------------
    # AWARENESS FUNNEL
    # ---------------------------------------------------
    elif funnel_stage == "Awareness":

        total_impressions = audience_df["Impressions"].sum()

        audience_df["Impression Share"] = safe_divide(
            audience_df["Impressions"],
            total_impressions,
            100
        )

        audience_df["Completion Index"] = safe_divide(
            audience_df["Completion Rate"],
            completion_rate
        )

        audience_df["CPM Efficiency"] = safe_divide(
            cpm,
            audience_df["CPM"]
        )

        audience_df["Confidence"] = np.select(
            [
                (
                    (audience_df["Spend Share"] >= 5)
                    & (audience_df["Impressions"] >= 1_000_000)
                ),
                (
                    (audience_df["Spend Share"] >= 2)
                    & (audience_df["Impressions"] >= 250_000)
                )
            ],
            ["High", "Medium"],
            default="Low"
        )

        recommendations = []
        reasons = []

        for _, row in audience_df.iterrows():

            spend_share = row["Spend Share"]
            impression_share = row["Impression Share"]
            impressions_value = row["Impressions"]
            completion_index = row["Completion Index"]
            cpm_efficiency = row["CPM Efficiency"]
            completion_value = row["Completion Rate"]
            segment_cpm = row["CPM"]
            confidence = row["Confidence"]

            if confidence == "Low":

                if (
                    completion_index >= 1.10
                    and cpm_efficiency >= 0.95
                ):
                    recommendation = "PROMISING - GATHER MORE DATA"
                    reason = (
                        f"Completion Index {completion_index:.2f} and "
                        f"CPM Efficiency {cpm_efficiency:.2f} are strong, "
                        f"but only {spend_share:.1f}% of spend and "
                        f"{impressions_value:,.0f} impressions are available."
                    )
                else:
                    recommendation = "INSUFFICIENT DATA"
                    reason = (
                        f"Only {spend_share:.1f}% of spend and "
                        f"{impressions_value:,.0f} impressions are available."
                    )

            elif (
                confidence == "High"
                and completion_index < 0.80
                and cpm_efficiency < 0.80
            ):
                recommendation = "NEGATION CANDIDATE"
                reason = (
                    f"Completion Index {completion_index:.2f} and "
                    f"CPM Efficiency {cpm_efficiency:.2f} both indicate "
                    f"material underperformance. Validate before exclusion."
                )

            elif (
                confidence == "High"
                and completion_index >= 1.10
                and cpm_efficiency >= 0.95
            ):
                recommendation = "SCALE"
                reason = (
                    f"{impression_share:.1f}% impression share on "
                    f"{spend_share:.1f}% spend share, with Completion Index "
                    f"{completion_index:.2f} and CPM Efficiency "
                    f"{cpm_efficiency:.2f}."
                )

            elif (
                completion_index >= 1.05
                and cpm_efficiency >= 0.90
            ):
                recommendation = "PRIORITIZE"
                reason = (
                    f"Completion Rate is {completion_value:.2f}% "
                    f"(Completion Index {completion_index:.2f}) while "
                    f"CPM remains reasonably efficient at ${segment_cpm:.2f}."
                )

            elif (
                completion_index < 0.90
                and cpm_efficiency < 0.90
            ):
                recommendation = "REDUCE"
                reason = (
                    f"Completion Index {completion_index:.2f} and "
                    f"CPM Efficiency {cpm_efficiency:.2f} are both weak."
                )

            elif (
                0.95 <= completion_index <= 1.05
                and 0.90 <= cpm_efficiency <= 1.10
            ):
                recommendation = "MAINTAIN"
                reason = (
                    f"Completion Index {completion_index:.2f} and "
                    f"CPM Efficiency {cpm_efficiency:.2f} are close to "
                    f"campaign average."
                )

            elif (
                completion_index < 0.95
                or cpm_efficiency < 0.90
            ):
                recommendation = "INVESTIGATE"
                reason = (
                    f"Completion Index is {completion_index:.2f} and "
                    f"CPM Efficiency is {cpm_efficiency:.2f}. One core "
                    f"awareness signal is weak."
                )

            else:
                recommendation = "WATCH"
                reason = (
                    f"Completion Index is {completion_index:.2f} and "
                    f"CPM Efficiency is {cpm_efficiency:.2f}. Signals are mixed."
                )

            recommendations.append(recommendation)
            reasons.append(reason)

        audience_df["Recommendation"] = recommendations
        audience_df["Reason"] = reasons

    else:

        audience_df["Recommendation"] = "Not Evaluated"
        audience_df["Confidence"] = "Low"
        audience_df["Reason"] = (
            "Campaign funnel stage is not assigned."
        )

    audience_df = apply_decision_support(audience_df, "audience")
    return audience_df


def render_analyzer_date_filter(source_df, page_key):
    """
    Let the trader analyze the full campaign, a specific month, a calendar
    week (Monday-Sunday), or a single day. Returns only the rows in the
    selected period while leaving the original campaign dataframe unchanged.
    """
    if source_df.empty or "Date" not in source_df.columns:
        return source_df.copy()

    dated_df = source_df.copy()
    dated_df["Date"] = pd.to_datetime(dated_df["Date"], errors="coerce")
    dated_df = dated_df[dated_df["Date"].notna()].copy()

    if dated_df.empty:
        st.warning("No valid dates are available for period filtering.")
        return source_df.copy()

    st.markdown("#### Optimization Period")
    period_type = st.radio(
        "Analyze",
        ["All Data", "Month", "Week", "Day"],
        horizontal=True,
        key=f"{page_key}_period_type"
    )

    filtered_df = dated_df.copy()
    period_label = "All available data"

    if period_type == "Month":
        month_periods = sorted(dated_df["Date"].dt.to_period("M").unique(), reverse=True)
        month_labels = [period.strftime("%B %Y") for period in month_periods]
        selected_label = st.selectbox(
            "Choose Month",
            month_labels,
            key=f"{page_key}_month"
        )
        selected_period = month_periods[month_labels.index(selected_label)]
        filtered_df = dated_df[dated_df["Date"].dt.to_period("M") == selected_period].copy()
        period_label = selected_label

    elif period_type == "Week":
        week_start = dated_df["Date"].dt.normalize() - pd.to_timedelta(
            dated_df["Date"].dt.weekday, unit="D"
        )
        week_starts = sorted(week_start.unique(), reverse=True)
        week_labels = [
            f"{pd.Timestamp(start).strftime('%b %d, %Y')} – "
            f"{(pd.Timestamp(start) + pd.Timedelta(days=6)).strftime('%b %d, %Y')}"
            for start in week_starts
        ]
        selected_label = st.selectbox(
            "Choose Week",
            week_labels,
            key=f"{page_key}_week"
        )
        selected_start = pd.Timestamp(week_starts[week_labels.index(selected_label)])
        selected_end = selected_start + pd.Timedelta(days=7)
        filtered_df = dated_df[
            (dated_df["Date"] >= selected_start)
            & (dated_df["Date"] < selected_end)
        ].copy()
        period_label = selected_label

    elif period_type == "Day":
        available_days = sorted(dated_df["Date"].dt.normalize().unique(), reverse=True)
        day_labels = [pd.Timestamp(day).strftime("%B %d, %Y") for day in available_days]
        selected_label = st.selectbox(
            "Choose Day",
            day_labels,
            key=f"{page_key}_day"
        )
        selected_day = pd.Timestamp(available_days[day_labels.index(selected_label)])
        filtered_df = dated_df[dated_df["Date"].dt.normalize() == selected_day].copy()
        period_label = selected_label

    st.caption(
        f"Analysis period: {period_label} • "
        f"{len(filtered_df):,} report rows included"
    )

    if filtered_df.empty:
        st.warning("No report rows are available for the selected period.")

    return filtered_df


def render_audience_recommendation_engine():
    """
    Render the simplified, decision-focused Audience Analyzer.
    """

    st.markdown(
        '<div class="section-label">Audience Analyzer</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Recommendations use only decision-relevant indices for the "
        "campaign objective. CTR and Viewability remain diagnostic "
        "metrics and do not drive the action recommendation."
    )

    analyzer_df = render_analyzer_date_filter(
        campaign_df,
        "audience"
    )

    if analyzer_df.empty:
        st.warning("No audience data is available for the selected period.")
        return

    audience_df = calculate_audience_recommendations(
        analyzer_df
    )

    if audience_df.empty:
        st.warning(
            "No audience data is available for the selected campaign."
        )
        return

    action_counts = (
        audience_df["Recommendation"]
        .value_counts()
    )

    scale_count = (
        action_counts.get("SCALE", 0)
        + action_counts.get("PRIORITIZE", 0)
    )

    maintain_count = (
        action_counts.get("MAINTAIN", 0)
        + action_counts.get("WATCH", 0)
    )

    review_count = (
        action_counts.get("INVESTIGATE", 0)
        + action_counts.get("REDUCE", 0)
    )

    negate_count = (
        action_counts.get("NEGATION CANDIDATE", 0)
    )

    render_tile_grid(
        [
            {
                "label": "Scale / Prioritize",
                "value": f"{scale_count}"
            },
            {
                "label": "Maintain / Watch",
                "value": f"{maintain_count}"
            },
            {
                "label": "Investigate / Reduce",
                "value": f"{review_count}"
            },
            {
                "label": "Negation Candidates",
                "value": f"{negate_count}"
            }
        ],
        compact=True
    )

    st.write("")

    recommendation_options = [
        "All",
        "SCALE",
        "PRIORITIZE",
        "MAINTAIN",
        "WATCH",
        "INVESTIGATE",
        "REDUCE",
        "NEGATION CANDIDATE",
        "PROMISING - GATHER MORE DATA",
        "INSUFFICIENT DATA"
    ]

    selected_recommendation = st.selectbox(
        "Filter Recommendation",
        recommendation_options,
        key="audience_recommendation_filter"
    )

    if selected_recommendation == "All":
        filtered_df = audience_df.copy()
    else:
        filtered_df = audience_df[
            audience_df["Recommendation"]
            == selected_recommendation
        ].copy()

    st.markdown(
        "#### Audience Decision Scorecard"
    )

    if funnel_stage == "Conversion":

        scorecard_columns = [
            "Audience_Segment",
            "Recommendation",
            "Evidence Strength",
            "Spend Share",
            "Conversion Share",
            "Revenue Share",
            "Efficiency Index",
            "CPA",
            "CPA Index",
            "ROAS",
            "ROAS Index",
            "Reason"
        ]

    else:

        scorecard_columns = [
            "Audience_Segment",
            "Recommendation",
            "Evidence Strength",
            "Spend Share",
            "Impression Share",
            "Completion Rate",
            "Completion Index",
            "CPM",
            "CPM Efficiency",
            "Reason"
        ]

    st.dataframe(
        format_dataframe_for_display(
            filtered_df[scorecard_columns]
        ),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "#### Decision Index by Audience"
    )

    if funnel_stage == "Conversion":
        decision_index_options = [
            "Efficiency Index",
            "CPA Index",
            "ROAS Index"
        ]
    else:
        decision_index_options = [
            "Completion Index",
            "CPM Efficiency"
        ]

    selected_decision_index = st.selectbox(
        "Decision Index",
        decision_index_options,
        key="audience_decision_index"
    )

    chart_df = audience_df[
        [
            "Audience_Segment",
            selected_decision_index,
            "Spend Share",
            "Recommendation",
            "Confidence"
        ]
    ].dropna(
        subset=[
            selected_decision_index
        ]
    ).sort_values(
        selected_decision_index,
        ascending=False
    )

    audience_order = chart_df[
        "Audience_Segment"
    ].tolist()

    audience_chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            y=alt.Y(
                "Audience_Segment:N",
                sort=audience_order,
                title="Audience"
            ),
            x=alt.X(
                f"{selected_decision_index}:Q",
                title=selected_decision_index
            ),
            tooltip=[
                alt.Tooltip(
                    "Audience_Segment:N",
                    title="Audience"
                ),
                alt.Tooltip(
                    f"{selected_decision_index}:Q",
                    title=selected_decision_index,
                    format=".2f"
                ),
                alt.Tooltip(
                    "Spend Share:Q",
                    title="Spend Share",
                    format=".2f"
                ),
                alt.Tooltip(
                    "Recommendation:N"
                ),
                alt.Tooltip(
                    "Confidence:N"
                )
            ]
        )
        .properties(
            height=max(
                320,
                min(
                    650,
                    len(chart_df) * 42
                )
            )
        )
    )

    st.altair_chart(
        audience_chart,
        use_container_width=True
    )

    with st.expander(
        "View Diagnostic Metrics"
    ):

        diagnostic_columns = [
            "Audience_Segment",
            "CTR",
            "Viewability",
            "Clicks",
            "CPC"
        ]

        st.dataframe(
            format_dataframe_for_display(
                audience_df[diagnostic_columns]
            ),
            use_container_width=True,
            hide_index=True
        )

    with st.expander(
        "How Audience Recommendations Are Determined"
    ):

        if funnel_stage == "Conversion":

            st.markdown(
                """
                **Conversion decision framework**

                **Decision inputs**
                - **Spend Share** = Audience Spend / Campaign Spend
                - **Conversion Share** = Audience Conversions / Campaign Conversions
                - **Efficiency Index** = Conversion Share / Spend Share
                - **CPA Index** = Campaign CPA / Audience CPA
                - **ROAS Index** = Audience ROAS / Campaign ROAS

                **Confidence**
                - High: Spend Share ≥ 5% and 30+ conversions
                - Medium: Spend Share ≥ 2% and 10+ conversions
                - Low: Below those thresholds

                **Not used in the recommendation**
                - CTR Index
                - Viewability Index
                - Blended Performance Index

                CTR, Viewability, and CPC remain diagnostic metrics only.
                """
            )

        else:

            st.markdown(
                """
                **Awareness decision framework**

                **Decision inputs**
                - **Spend Share** = Audience Spend / Campaign Spend
                - **Impression Share** = Audience Impressions / Campaign Impressions
                - **Completion Index** = Audience Completion Rate / Campaign Completion Rate
                - **CPM Efficiency** = Campaign CPM / Audience CPM

                **Confidence**
                - High: Spend Share ≥ 5% and 1M+ impressions
                - Medium: Spend Share ≥ 2% and 250K+ impressions
                - Low: Below those thresholds

                **Not used in the recommendation**
                - CTR Index
                - Viewability Index
                - Blended Performance Index

                CTR and Viewability remain diagnostic metrics only unless
                the campaign objective explicitly changes.
                """
            )



def calculate_specialized_dimension_recommendations(
    data,
    dimension_column,
    analyzer_type,
    metadata_columns=None
):
    """
    Decision engine for Creative, Inventory, and Domain / Website.

    The engine intentionally keeps only metrics and indices that
    should influence decisions for that analyzer.

    analyzer_type:
    - "creative"
    - "inventory"
    - "domain"

    CONVERSION OBJECTIVE
    --------------------
    Decision inputs for all three analyzers:
    - Spend Share
    - Conversion Share
    - Revenue Share
    - Efficiency Index = Conversion Share / Spend Share
    - CPA Index = Campaign CPA / Segment CPA
    - ROAS Index = Segment ROAS / Campaign ROAS

    AWARENESS OBJECTIVE
    -------------------
    Creative:
    - Completion Index only
      (plus Spend Share / Impression Share for scale and evidence)

    Inventory:
    - Completion Index
    - Viewability Index
    - CPM Efficiency

    Domain / Website:
    - Completion Index
    - Viewability Index
    - CPM Efficiency

    No blended Performance Index is used.
    CTR and CPC are diagnostic unless the campaign objective
    explicitly changes to optimize toward engagement.
    """

    result = aggregate_dimension_performance(
        data,
        dimension_column,
        metadata_columns
    )

    if result.empty:
        return result

    # ---------------------------------------------------
    # Universal share metrics
    # ---------------------------------------------------

    total_spend = result["Spend"].sum()
    total_impressions = result["Impressions"].sum()

    result["Spend Share"] = safe_divide(
        result["Spend"],
        total_spend,
        100
    )

    result["Impression Share"] = safe_divide(
        result["Impressions"],
        total_impressions,
        100
    )

    # ---------------------------------------------------
    # Conversion objective
    # ---------------------------------------------------

    if funnel_stage == "Conversion":

        total_conversions = result["Total Conversions"].sum()
        total_revenue = result["Revenue"].sum()

        result["Conversion Share"] = safe_divide(
            result["Total Conversions"],
            total_conversions,
            100
        )

        result["Revenue Share"] = safe_divide(
            result["Revenue"],
            total_revenue,
            100
        )

        result["Efficiency Index"] = safe_divide(
            result["Conversion Share"],
            result["Spend Share"]
        )

        result["CPA Index"] = safe_divide(
            cpa,
            result["CPA"]
        )

        result["ROAS Index"] = safe_divide(
            result["ROAS"],
            roas
        )

        # Evidence / confidence:
        # High   = >=5% spend share and >=30 conversions
        # Medium = >=2% spend share and >=10 conversions
        # Low    = everything else
        result["Confidence"] = np.select(
            [
                (
                    (result["Spend Share"] >= 5)
                    & (result["Total Conversions"] >= 30)
                ),
                (
                    (result["Spend Share"] >= 2)
                    & (result["Total Conversions"] >= 10)
                )
            ],
            ["High", "Medium"],
            default="Low"
        )

        recommendations = []
        reasons = []

        for _, row in result.iterrows():

            spend_share = row["Spend Share"]
            conversion_share = row["Conversion Share"]
            revenue_share = row["Revenue Share"]
            conversions = row["Total Conversions"]
            efficiency = row["Efficiency Index"]
            cpa_index = row["CPA Index"]
            roas_index = row["ROAS Index"]
            confidence = row["Confidence"]

            # Analyzer-specific negative action label
            if analyzer_type == "creative":
                severe_action = "PAUSE CANDIDATE"
                reduce_action = "REFRESH / REDUCE"
            elif analyzer_type == "domain":
                severe_action = "NEGATION CANDIDATE"
                reduce_action = "REDUCE"
            else:
                severe_action = "AVOID / REDUCE"
                reduce_action = "REDUCE"

            if confidence == "Low":

                if (
                    pd.notna(efficiency)
                    and efficiency >= 1.20
                    and (
                        cpa_index >= 1.00
                        or roas_index >= 1.00
                    )
                    and conversions > 0
                ):
                    recommendation = "PROMISING - GATHER MORE DATA"
                    reason = (
                        f"{conversion_share:.1f}% conversion share on "
                        f"{spend_share:.1f}% spend share "
                        f"(Efficiency Index {efficiency:.2f}), but "
                        f"confidence is low."
                    )
                else:
                    recommendation = "INSUFFICIENT DATA"
                    reason = (
                        f"Spend Share is {spend_share:.1f}% with "
                        f"{conversions:,.0f} conversions. More evidence "
                        f"is needed before taking action."
                    )

            elif (
                confidence == "High"
                and efficiency < 0.40
                and cpa_index < 0.75
                and roas_index < 0.75
            ):
                recommendation = severe_action
                reason = (
                    f"Only {conversion_share:.1f}% of conversions come "
                    f"from {spend_share:.1f}% of spend. Efficiency Index "
                    f"is {efficiency:.2f}, CPA Index {cpa_index:.2f}, "
                    f"and ROAS Index {roas_index:.2f}."
                )

            elif (
                confidence == "High"
                and efficiency >= 1.20
                and cpa_index >= 1.10
                and roas_index >= 1.10
            ):
                recommendation = "SCALE"
                reason = (
                    f"{conversion_share:.1f}% conversion share and "
                    f"{revenue_share:.1f}% revenue share on "
                    f"{spend_share:.1f}% spend share. Efficiency Index "
                    f"{efficiency:.2f}, CPA Index {cpa_index:.2f}, "
                    f"ROAS Index {roas_index:.2f}."
                )

            elif (
                efficiency >= 1.10
                and (
                    cpa_index >= 1.00
                    or roas_index >= 1.00
                )
            ):
                recommendation = "PRIORITIZE"
                reason = (
                    f"Conversion contribution exceeds spend allocation: "
                    f"{conversion_share:.1f}% conversion share versus "
                    f"{spend_share:.1f}% spend share "
                    f"(Efficiency Index {efficiency:.2f})."
                )

            elif (
                efficiency < 0.75
                and cpa_index < 0.90
                and roas_index < 0.90
            ):
                recommendation = reduce_action
                reason = (
                    f"Efficiency Index {efficiency:.2f}, CPA Index "
                    f"{cpa_index:.2f}, and ROAS Index {roas_index:.2f} "
                    f"all indicate underperformance."
                )

            elif (
                0.90 <= efficiency <= 1.10
                and 0.90 <= cpa_index <= 1.10
                and 0.90 <= roas_index <= 1.10
            ):
                recommendation = "MAINTAIN"
                reason = (
                    f"Efficiency Index {efficiency:.2f}, CPA Index "
                    f"{cpa_index:.2f}, and ROAS Index {roas_index:.2f} "
                    f"are close to campaign average."
                )

            elif efficiency < 0.90:
                recommendation = "INVESTIGATE"
                reason = (
                    f"Conversion Share ({conversion_share:.1f}%) trails "
                    f"Spend Share ({spend_share:.1f}%). Investigate the "
                    f"underlying driver before reducing."
                )

            else:
                recommendation = "WATCH"
                reason = (
                    f"Signals are mixed: Efficiency Index {efficiency:.2f}, "
                    f"CPA Index {cpa_index:.2f}, ROAS Index "
                    f"{roas_index:.2f}."
                )

            recommendations.append(recommendation)
            reasons.append(reason)

        result["Recommendation"] = recommendations
        result["Reason"] = reasons

    # ---------------------------------------------------
    # Awareness objective
    # ---------------------------------------------------

    elif funnel_stage == "Awareness":

        result["Completion Index"] = safe_divide(
            result["Completion Rate"],
            completion_rate
        )

        # Creative should be judged primarily on the response to
        # the creative itself. CPM and Viewability are driven more
        # by inventory / supply than by the creative asset.
        if analyzer_type in ["inventory", "domain"]:

            result["Viewability Index"] = safe_divide(
                result["Viewability"],
                campaign_viewability
            )

            result["CPM Efficiency"] = safe_divide(
                cpm,
                result["CPM"]
            )

        # Awareness evidence:
        # High   = >=5% spend share and >=1M impressions
        # Medium = >=2% spend share and >=250K impressions
        # Low    = everything else
        result["Confidence"] = np.select(
            [
                (
                    (result["Spend Share"] >= 5)
                    & (result["Impressions"] >= 1_000_000)
                ),
                (
                    (result["Spend Share"] >= 2)
                    & (result["Impressions"] >= 250_000)
                )
            ],
            ["High", "Medium"],
            default="Low"
        )

        recommendations = []
        reasons = []

        for _, row in result.iterrows():

            spend_share = row["Spend Share"]
            impression_share = row["Impression Share"]
            impressions_value = row["Impressions"]
            confidence = row["Confidence"]
            completion_index = row["Completion Index"]
            completion_value = row["Completion Rate"]

            # ---------------------------------------------------
            # Creative awareness rules
            # ---------------------------------------------------
            if analyzer_type == "creative":

                if confidence == "Low":

                    if completion_index >= 1.10:
                        recommendation = "PROMISING - GATHER MORE DATA"
                        reason = (
                            f"Completion Index is {completion_index:.2f}, "
                            f"but the creative has only {spend_share:.1f}% "
                            f"of spend and {impressions_value:,.0f} impressions."
                        )
                    else:
                        recommendation = "INSUFFICIENT DATA"
                        reason = (
                            f"Only {spend_share:.1f}% of spend and "
                            f"{impressions_value:,.0f} impressions are "
                            f"available for this creative."
                        )

                elif (
                    confidence == "High"
                    and completion_index < 0.80
                ):
                    recommendation = "PAUSE CANDIDATE"
                    reason = (
                        f"Completion Rate is {completion_value:.2f}% "
                        f"(Completion Index {completion_index:.2f}), "
                        f"materially below campaign average."
                    )

                elif (
                    confidence == "High"
                    and completion_index >= 1.10
                ):
                    recommendation = "SCALE"
                    reason = (
                        f"The creative receives {spend_share:.1f}% of spend "
                        f"and {impression_share:.1f}% of impressions while "
                        f"delivering a Completion Index of "
                        f"{completion_index:.2f}."
                    )

                elif completion_index >= 1.05:
                    recommendation = "PRIORITIZE"
                    reason = (
                        f"Completion Rate is {completion_value:.2f}% "
                        f"(Completion Index {completion_index:.2f}), "
                        f"above campaign average."
                    )

                elif completion_index < 0.90:
                    recommendation = "REFRESH / REDUCE"
                    reason = (
                        f"Completion Index is {completion_index:.2f}, "
                        f"indicating materially weaker creative completion."
                    )

                elif 0.95 <= completion_index <= 1.05:
                    recommendation = "MAINTAIN"
                    reason = (
                        f"Completion Index is {completion_index:.2f}, "
                        f"close to campaign average."
                    )

                else:
                    recommendation = "WATCH"
                    reason = (
                        f"Completion Index is {completion_index:.2f}. "
                        f"Continue monitoring before changing rotation."
                    )

            # ---------------------------------------------------
            # Inventory / Domain awareness rules
            # ---------------------------------------------------
            else:

                viewability_index = row["Viewability Index"]
                cpm_efficiency = row["CPM Efficiency"]
                viewability_value = row["Viewability"]
                segment_cpm = row["CPM"]

                if analyzer_type == "domain":
                    severe_action = "NEGATION CANDIDATE"
                else:
                    severe_action = "AVOID / REDUCE"

                if confidence == "Low":

                    if (
                        completion_index >= 1.10
                        and viewability_index >= 1.05
                        and cpm_efficiency >= 0.95
                    ):
                        recommendation = "PROMISING - GATHER MORE DATA"
                        reason = (
                            f"Completion Index {completion_index:.2f}, "
                            f"Viewability Index {viewability_index:.2f}, "
                            f"and CPM Efficiency {cpm_efficiency:.2f} are "
                            f"strong, but evidence is still limited."
                        )
                    else:
                        recommendation = "INSUFFICIENT DATA"
                        reason = (
                            f"Only {spend_share:.1f}% of spend and "
                            f"{impressions_value:,.0f} impressions are "
                            f"available."
                        )

                elif (
                    confidence == "High"
                    and completion_index < 0.80
                    and viewability_index < 0.80
                    and cpm_efficiency < 0.80
                ):
                    recommendation = severe_action
                    reason = (
                        f"Completion Index {completion_index:.2f}, "
                        f"Viewability Index {viewability_index:.2f}, and "
                        f"CPM Efficiency {cpm_efficiency:.2f} all show "
                        f"material underperformance."
                    )

                elif (
                    confidence == "High"
                    and completion_index >= 1.10
                    and viewability_index >= 1.05
                    and cpm_efficiency >= 0.95
                ):
                    recommendation = "SCALE"
                    reason = (
                        f"{impression_share:.1f}% impression share on "
                        f"{spend_share:.1f}% spend share, with Completion "
                        f"Index {completion_index:.2f}, Viewability Index "
                        f"{viewability_index:.2f}, and CPM Efficiency "
                        f"{cpm_efficiency:.2f}."
                    )

                elif (
                    completion_index >= 1.05
                    and viewability_index >= 1.00
                    and cpm_efficiency >= 0.90
                ):
                    recommendation = "PRIORITIZE"
                    reason = (
                        f"Completion Index {completion_index:.2f}, "
                        f"Viewability Index {viewability_index:.2f}, and "
                        f"CPM Efficiency {cpm_efficiency:.2f} indicate "
                        f"above-average quality at reasonable cost."
                    )

                elif (
                    completion_index < 0.90
                    and viewability_index < 0.90
                    and cpm_efficiency < 0.90
                ):
                    recommendation = "REDUCE"
                    reason = (
                        f"Completion, Viewability, and CPM efficiency are "
                        f"all below campaign norms: "
                        f"{completion_index:.2f}, "
                        f"{viewability_index:.2f}, "
                        f"{cpm_efficiency:.2f}."
                    )

                elif (
                    0.95 <= completion_index <= 1.05
                    and 0.95 <= viewability_index <= 1.05
                    and 0.90 <= cpm_efficiency <= 1.10
                ):
                    recommendation = "MAINTAIN"
                    reason = (
                        f"Completion Index {completion_index:.2f}, "
                        f"Viewability Index {viewability_index:.2f}, and "
                        f"CPM Efficiency {cpm_efficiency:.2f} are close "
                        f"to campaign average."
                    )

                elif (
                    completion_index < 0.95
                    or viewability_index < 0.95
                    or cpm_efficiency < 0.90
                ):
                    recommendation = "INVESTIGATE"
                    reason = (
                        f"One or more inventory-quality signals are weak: "
                        f"Completion {completion_index:.2f}, Viewability "
                        f"{viewability_index:.2f}, CPM Efficiency "
                        f"{cpm_efficiency:.2f}."
                    )

                else:
                    recommendation = "WATCH"
                    reason = (
                        f"Signals are mixed: Completion Index "
                        f"{completion_index:.2f}, Viewability Index "
                        f"{viewability_index:.2f}, CPM Efficiency "
                        f"{cpm_efficiency:.2f}."
                    )

            recommendations.append(recommendation)
            reasons.append(reason)

        result["Recommendation"] = recommendations
        result["Reason"] = reasons

    else:

        result["Recommendation"] = "Not Evaluated"
        result["Confidence"] = "Low"
        result["Reason"] = "Campaign funnel stage is not assigned."

    result = apply_decision_support(result, analyzer_type)
    return result


def render_specialized_decision_analyzer(
    title,
    dimension_column,
    dimension_label,
    page_key,
    analyzer_type,
    metadata_columns=None,
    context_note=None
):
    """
    Render Creative, Inventory, or Domain decision analyzer.
    """

    st.markdown(
        f'<div class="section-label">{title}</div>',
        unsafe_allow_html=True
    )

    if context_note:
        st.info(context_note)

    analyzer_df = render_analyzer_date_filter(
        campaign_df,
        page_key
    )

    if analyzer_df.empty:
        st.warning(
            f"No {dimension_label.lower()} data is available "
            f"for the selected period."
        )
        return

    result = calculate_specialized_dimension_recommendations(
        analyzer_df,
        dimension_column,
        analyzer_type,
        metadata_columns
    )

    if result.empty:
        st.warning(
            f"No {dimension_label.lower()} data is available "
            f"for the selected campaign."
        )
        return

    # ---------------------------------------------------
    # Action summary
    # ---------------------------------------------------

    actions = result["Recommendation"].value_counts()

    positive_count = (
        actions.get("SCALE", 0)
        + actions.get("PRIORITIZE", 0)
    )

    neutral_count = (
        actions.get("MAINTAIN", 0)
        + actions.get("WATCH", 0)
    )

    review_count = (
        actions.get("INVESTIGATE", 0)
        + actions.get("REDUCE", 0)
        + actions.get("REFRESH / REDUCE", 0)
    )

    severe_count = (
        actions.get("NEGATION CANDIDATE", 0)
        + actions.get("PAUSE CANDIDATE", 0)
        + actions.get("AVOID / REDUCE", 0)
    )

    render_tile_grid(
        [
            {
                "label": "Scale / Prioritize",
                "value": f"{positive_count}"
            },
            {
                "label": "Maintain / Watch",
                "value": f"{neutral_count}"
            },
            {
                "label": "Investigate / Reduce",
                "value": f"{review_count}"
            },
            {
                "label": "Strong Action Candidates",
                "value": f"{severe_count}"
            }
        ],
        compact=True
    )

    st.write("")

    # ---------------------------------------------------
    # Recommendation filter
    # ---------------------------------------------------

    available_actions = (
        ["All"]
        + sorted(
            result["Recommendation"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    selected_action = st.selectbox(
        "Filter Recommendation",
        available_actions,
        key=f"{page_key}_recommendation_filter"
    )

    if selected_action == "All":
        filtered = result.copy()
    else:
        filtered = result[
            result["Recommendation"] == selected_action
        ].copy()

    # ---------------------------------------------------
    # Decision scorecard
    # ---------------------------------------------------

    st.markdown(
        f"#### {dimension_label} Decision Scorecard"
    )

    base_columns = [dimension_column]

    for metadata_column in (metadata_columns or []):
        if metadata_column in result.columns:
            base_columns.append(metadata_column)

    if funnel_stage == "Conversion":

        scorecard_columns = (
            base_columns
            + [
                "Recommendation",
                "Evidence Strength",
                "Spend Share",
                "Conversion Share",
                "Revenue Share",
                "Efficiency Index",
                "CPA",
                "CPA Index",
                "ROAS",
                "ROAS Index",
                "Reason"
            ]
        )

        decision_index_options = [
            "Efficiency Index",
            "CPA Index",
            "ROAS Index"
        ]

    elif analyzer_type == "creative":

        scorecard_columns = (
            base_columns
            + [
                "Recommendation",
                "Evidence Strength",
                "Spend Share",
                "Impression Share",
                "Completion Rate",
                "Completion Index",
                "Reason"
            ]
        )

        decision_index_options = [
            "Completion Index"
        ]

    else:

        scorecard_columns = (
            base_columns
            + [
                "Recommendation",
                "Evidence Strength",
                "Spend Share",
                "Impression Share",
                "Completion Rate",
                "Completion Index",
                "Viewability",
                "Viewability Index",
                "CPM",
                "CPM Efficiency",
                "Reason"
            ]
        )

        decision_index_options = [
            "Completion Index",
            "Viewability Index",
            "CPM Efficiency"
        ]

    st.dataframe(
        format_dataframe_for_display(filtered[scorecard_columns]),
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------
    # Decision index chart
    # ---------------------------------------------------

    st.markdown(
        f"#### Decision Index by {dimension_label}"
    )

    selected_index = st.selectbox(
        "Decision Index",
        decision_index_options,
        key=f"{page_key}_decision_index"
    )

    chart_df = result[
        [
            dimension_column,
            selected_index,
            "Spend Share",
            "Recommendation",
            "Confidence"
        ]
    ].dropna(
        subset=[selected_index]
    ).sort_values(
        selected_index,
        ascending=False
    )

    order = chart_df[dimension_column].tolist()

    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            y=alt.Y(
                f"{dimension_column}:N",
                sort=order,
                title=dimension_label
            ),
            x=alt.X(
                f"{selected_index}:Q",
                title=selected_index
            ),
            tooltip=[
                alt.Tooltip(
                    f"{dimension_column}:N",
                    title=dimension_label
                ),
                alt.Tooltip(
                    f"{selected_index}:Q",
                    title=selected_index,
                    format=".2f"
                ),
                alt.Tooltip(
                    "Spend Share:Q",
                    title="Spend Share",
                    format=".2f"
                ),
                alt.Tooltip(
                    "Recommendation:N"
                ),
                alt.Tooltip(
                    "Confidence:N"
                )
            ]
        )
        .properties(
            height=max(
                320,
                min(
                    700,
                    len(chart_df) * 40
                )
            )
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )

    # ---------------------------------------------------
    # Diagnostic metrics
    # ---------------------------------------------------

    with st.expander(
        "View Diagnostic Metrics"
    ):

        if analyzer_type == "creative":

            diagnostics = [
                dimension_column,
                "CTR",
                "Clicks",
                "CPC",
                "Viewability"
            ]

        else:

            diagnostics = [
                dimension_column,
                "CTR",
                "Clicks",
                "CPC"
            ]

            # For conversion inventory/domain, viewability and completion
            # are useful for investigation but do not drive the action.
            if funnel_stage == "Conversion":
                diagnostics += [
                    "Viewability",
                    "Completion Rate"
                ]

        # Include metadata such as creative length.
        for metadata_column in (metadata_columns or []):
            if (
                metadata_column in result.columns
                and metadata_column not in diagnostics
            ):
                diagnostics.insert(1, metadata_column)

        diagnostics = [
            column
            for column in diagnostics
            if column in result.columns
        ]

        st.dataframe(
            format_dataframe_for_display(result[diagnostics]),
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------------
    # Explain the decision framework
    # ---------------------------------------------------

    with st.expander(
        f"How {dimension_label} Recommendations Are Determined"
    ):

        if funnel_stage == "Conversion":

            st.markdown(
                """
                **Conversion decision inputs**
                - Spend Share
                - Conversion Share
                - Revenue Share
                - Efficiency Index = Conversion Share / Spend Share
                - CPA Index = Campaign CPA / Segment CPA
                - ROAS Index = Segment ROAS / Campaign ROAS

                **Not used to drive the recommendation**
                - CTR Index
                - Viewability Index
                - Completion Index
                - Blended Performance Index

                CTR, Viewability, Completion Rate, and CPC are retained
                only for diagnosis after a segment is flagged.
                """
            )

        elif analyzer_type == "creative":

            st.markdown(
                """
                **Awareness creative decision inputs**
                - Spend Share / Impression Share for scale and evidence
                - Completion Index = Creative Completion Rate / Campaign Completion Rate

                **Not used to drive the recommendation**
                - CPM Index
                - CTR Index
                - Viewability Index
                - Blended Performance Index

                This avoids penalizing a creative for supply-side metrics
                that the creative itself does not control.
                """
            )

        else:

            st.markdown(
                """
                **Awareness supply decision inputs**
                - Spend Share / Impression Share for scale and evidence
                - Completion Index
                - Viewability Index
                - CPM Efficiency = Campaign CPM / Segment CPM

                These metrics directly describe awareness delivery quality
                and supply cost for Inventory / Domain analysis.

                **Not used to drive the recommendation**
                - CTR Index
                - CPC Index
                - Blended Performance Index
                """
            )


def get_dimension_metric_options():
    """
    Return funnel-specific metrics for detailed analyzers.
    """

    if funnel_stage == "Awareness":

        return {
            "Completion Rate": "Completion Rate",
            "Impressions": "Impressions",
            "Spend": "Spend",
            "CPM": "CPM",
            "Viewability": "Viewability",
            "CTR": "CTR",
            "CPC": "CPC"
        }

    elif funnel_stage == "Conversion":

        return {
            "CPA": "CPA",
            "ROAS": "ROAS",
            "Total Conversions": "Total Conversions",
            "Revenue": "Revenue",
            "Spend": "Spend",
            "Conversion Rate": "Conversion Rate",
            "CTR": "CTR",
            "CPC": "CPC"
        }

    return {
        "Spend": "Spend"
    }


def format_analysis_value(metric_name, value):
    """Use the global dashboard formatting standard."""
    return format_metric_value(metric_name, value)



def render_dimension_analyzer(
    title,
    dimension_column,
    dimension_label,
    page_key,
    metadata_columns=None,
    context_note=None
):
    """
    Render one reusable detailed analyzer page.

    The same function powers Audience, Creative, and
    Domain / Website pages.
    """

    st.markdown(
        f'<div class="section-label">{title}</div>',
        unsafe_allow_html=True
    )

    if context_note:
        st.info(context_note)


    analysis_df = aggregate_dimension_performance(
        campaign_df,
        dimension_column,
        metadata_columns
    )


    if analysis_df.empty:

        st.warning(
            f"No {dimension_label.lower()} data is available "
            f"for the selected campaign."
        )

        return


    # ---------------------------------------------------
    # TOP SUMMARY TILES
    # ---------------------------------------------------

    attention_count = (
        analysis_df["Status"]
        != "Strong"
    ).sum()

    top_spend_row = analysis_df.loc[
        analysis_df["Spend"].idxmax()
    ]


    if funnel_stage == "Awareness":

        primary_metric_label = "Campaign Completion Rate"
        primary_metric_value = format_percent(completion_rate)

    else:

        primary_metric_label = "Campaign CPA"
        primary_metric_value = format_currency(cpa)


    render_tile_grid(
        [
            {
                "label": f"{dimension_label}s Analyzed",
                "value": format_compact_number(len(analysis_df))
            },
            {
                "label": "Highest Spend",
                "value": format_currency(top_spend_row["Spend"]),
                "note": str(
                    top_spend_row[dimension_column]
                )
            },
            {
                "label": primary_metric_label,
                "value": primary_metric_value
            },
            {
                "label": "Areas to Review",
                "value": format_compact_number(attention_count),
                "note": "Watch + Needs Attention"
            }
        ],
        compact=True
    )


    st.write("")


    # ---------------------------------------------------
    # METRIC SELECTOR + PERFORMANCE CHART
    # ---------------------------------------------------

    metric_options = get_dimension_metric_options()

    selected_metric_label = st.selectbox(
        "Analyze by Metric",
        list(metric_options.keys()),
        key=f"{page_key}_metric"
    )

    selected_metric_column = metric_options[
        selected_metric_label
    ]


    chart_df = analysis_df[
        [
            dimension_column,
            selected_metric_column,
            "Spend",
            "Impressions",
            "Status"
        ]
    ].dropna(
        subset=[selected_metric_column]
    ).copy()


    # Lower values are preferable for CPA and CPC.
    # All other charts are sorted highest-to-lowest because
    # the chart is descriptive rather than an overall ranking.

    lower_is_better = (
        selected_metric_label
        in ["CPA", "CPC"]
    )

    chart_df = chart_df.sort_values(
        selected_metric_column,
        ascending=lower_is_better
    ).head(15)


    category_order = chart_df[
        dimension_column
    ].tolist()


    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            y=alt.Y(
                f"{dimension_column}:N",
                sort=category_order,
                title=dimension_label
            ),
            x=alt.X(
                f"{selected_metric_column}:Q",
                title=selected_metric_label
            ),
            tooltip=[
                alt.Tooltip(
                    f"{dimension_column}:N",
                    title=dimension_label
                ),
                alt.Tooltip(
                    f"{selected_metric_column}:Q",
                    title=selected_metric_label,
                    format=",.2f"
                ),
                alt.Tooltip(
                    "Spend:Q",
                    title="Spend",
                    format="$,.2f"
                ),
                alt.Tooltip(
                    "Impressions:Q",
                    title="Impressions",
                    format=",.0f"
                ),
                alt.Tooltip(
                    "Status:N",
                    title="Status"
                )
            ]
        )
        .properties(
            height=max(
                320,
                min(
                    650,
                    len(chart_df) * 38
                )
            )
        )
    )


    st.altair_chart(
        chart,
        use_container_width=True
    )


    # ---------------------------------------------------
    # INVESTIGATION QUEUE
    # ---------------------------------------------------
    # This section identifies dimensions that deserve further
    # inspection according to the same funnel-stage rules.

    st.markdown(
        "#### Investigation Queue"
    )


    investigation_df = analysis_df[
        analysis_df["Status"]
        != "Strong"
    ].copy()


    if investigation_df.empty:

        st.success(
            f"No {dimension_label.lower()} groups are currently "
            f"flagged by the prototype target rules."
        )

    else:

        investigation_df = investigation_df.sort_values(
            "Spend",
            ascending=False
        )


        if funnel_stage == "Awareness":

            investigation_columns = [
                dimension_column,
                "Status",
                "Spend",
                "Impressions",
                "CPM",
                "Completion Rate",
                "Viewability",
                "CTR"
            ]

        else:

            investigation_columns = [
                dimension_column,
                "Status",
                "Spend",
                "Total Conversions",
                "CPA",
                "Revenue",
                "ROAS",
                "Conversion Rate"
            ]


        st.dataframe(
            format_dataframe_for_display(
                investigation_df[investigation_columns]
            ),
            use_container_width=True,
            hide_index=True
        )


    # ---------------------------------------------------
    # FULL PERFORMANCE TABLE
    # ---------------------------------------------------

    with st.expander(
        f"View Full {dimension_label} Performance Data"
    ):

        base_columns = [
            dimension_column
        ]

        for metadata_column in (
            metadata_columns or []
        ):

            if metadata_column in analysis_df.columns:
                base_columns.append(
                    metadata_column
                )


        if funnel_stage == "Awareness":

            table_columns = (
                base_columns
                + [
                    "Status",
                    "Spend",
                    "Impressions",
                    "CPM",
                    "Completion Rate",
                    "Viewability",
                    "Clicks",
                    "CTR",
                    "CPC"
                ]
            )

        else:

            table_columns = (
                base_columns
                + [
                    "Status",
                    "Spend",
                    "Impressions",
                    "Clicks",
                    "Total Conversions",
                    "CPA",
                    "Conversion Rate",
                    "Revenue",
                    "ROAS",
                    "CTR",
                    "CPC"
                ]
            )


        st.dataframe(
            format_dataframe_for_display(
                analysis_df[table_columns]
            ),
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------------------
# END SECTION 18
# ---------------------------------------------------

# ---------------------------------------------------
# SECTION 19: BUILD MONTHLY PERFORMANCE DATA
# ---------------------------------------------------

monthly_source = campaign_df.dropna(
    subset=["Date"]
).copy()

monthly_source["Month_Date"] = (
    monthly_source["Date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

monthly_summary = (
    monthly_source
    .groupby("Month_Date", as_index=False)
    .agg(
        Spend=("Spend_USD", "sum"),
        Impressions=("Impressions_Served", "sum"),
        Clicks=("Clicks", "sum"),
        View_Through_Conversions=("Conv_View_Through", "sum"),
        Click_Through_Conversions=("Conv_Click_Through", "sum"),
        Revenue=("Revenue_Attributed_USD", "sum"),
        Completion_Rate=("Completion_Rate_%", "mean")
    )
    .sort_values("Month_Date")
    .reset_index(drop=True)
)

monthly_summary["Month"] = (
    monthly_summary["Month_Date"]
    .dt.strftime("%b %Y")
)

monthly_summary["Total Conversions"] = (
    monthly_summary["View_Through_Conversions"]
    + monthly_summary["Click_Through_Conversions"]
)

monthly_summary["CPM"] = 0.0
monthly_summary["CTR"] = 0.0
monthly_summary["CPC"] = 0.0
monthly_summary["CPA"] = 0.0
monthly_summary["Conversion Rate"] = 0.0
monthly_summary["ROAS"] = 0.0


valid_impressions = (
    monthly_summary["Impressions"] > 0
)

monthly_summary.loc[
    valid_impressions,
    "CPM"
] = (
    monthly_summary.loc[
        valid_impressions,
        "Spend"
    ]
    / monthly_summary.loc[
        valid_impressions,
        "Impressions"
    ]
) * 1000

monthly_summary.loc[
    valid_impressions,
    "CTR"
] = (
    monthly_summary.loc[
        valid_impressions,
        "Clicks"
    ]
    / monthly_summary.loc[
        valid_impressions,
        "Impressions"
    ]
) * 100


valid_clicks = (
    monthly_summary["Clicks"] > 0
)

monthly_summary.loc[
    valid_clicks,
    "CPC"
] = (
    monthly_summary.loc[
        valid_clicks,
        "Spend"
    ]
    / monthly_summary.loc[
        valid_clicks,
        "Clicks"
    ]
)

monthly_summary.loc[
    valid_clicks,
    "Conversion Rate"
] = (
    monthly_summary.loc[
        valid_clicks,
        "Click_Through_Conversions"
    ]
    / monthly_summary.loc[
        valid_clicks,
        "Clicks"
    ]
) * 100


valid_conversions = (
    monthly_summary["Total Conversions"] > 0
)

monthly_summary.loc[
    valid_conversions,
    "CPA"
] = (
    monthly_summary.loc[
        valid_conversions,
        "Spend"
    ]
    / monthly_summary.loc[
        valid_conversions,
        "Total Conversions"
    ]
)


valid_spend = (
    monthly_summary["Spend"] > 0
)

monthly_summary.loc[
    valid_spend,
    "ROAS"
] = (
    monthly_summary.loc[
        valid_spend,
        "Revenue"
    ]
    / monthly_summary.loc[
        valid_spend,
        "Spend"
    ]
)

# ---------------------------------------------------
# END SECTION 19
# ---------------------------------------------------



# ---------------------------------------------------
# PROFESSIONAL UI / UX ENHANCEMENTS
# ---------------------------------------------------
# A compact design system and decision-support layer shared across TradeIQ.

st.markdown("""
<style>
/* ---------- Sidebar visual polish only ---------- */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.15rem;
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-left: 0.35rem;
    padding-right: 0.35rem;
}

/* Keep sidebar content aligned to one visual grid */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stRadio"],
section[data-testid="stSidebar"] [data-testid="stExpander"] {
    width: 100%;
}

/* Cleaner section headings without changing text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    margin-top: 0.65rem;
    margin-bottom: 0.45rem;
    letter-spacing: -0.01em;
}

section[data-testid="stSidebar"] h3 {
    font-size: 1rem;
}

/* Uniform select boxes */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    min-height: 2.75rem;
    border-radius: 10px;
}

/* Report Upload and other expanders */
section[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 11px;
    overflow: hidden;
    margin-bottom: 0.65rem;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    min-height: 2.7rem;
    padding-top: 0.15rem;
    padding-bottom: 0.15rem;
    font-weight: 650;
}

/* Navigation: same radio functionality, cleaner alignment and spacing */
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0.08rem;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    min-height: 1.9rem;
    margin: 0;
    padding: 0.16rem 0.15rem;
    border-radius: 7px;
    align-items: center;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    line-height: 1.2;
    margin: 0;
}

/* Make radio circles visually consistent */
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    margin-top: 0;
}

/* Cleaner horizontal rules */
section[data-testid="stSidebar"] hr {
    margin: 1rem 0;
    border-color: rgba(255,255,255,0.09);
}

/* Reduce large default vertical gaps between sidebar blocks */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.65rem;
}

/* File/report status text stays compact */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    margin-top: -0.15rem;
    margin-bottom: 0.25rem;
}

/* Buttons fill their intended area and share the same geometry */
section[data-testid="stSidebar"] .stButton > button {
    min-height: 2.55rem;
    border-radius: 9px;
}

/* Prevent long campaign/report names from visually breaking the sidebar */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    overflow-wrap: anywhere;
}

/* Keep sidebar usable at common laptop heights */
@media (max-height: 850px) {
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.48rem;
    }
    section[data-testid="stSidebar"] hr {
        margin: 0.72rem 0;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        min-height: 1.7rem;
        padding-top: 0.10rem;
        padding-bottom: 0.10rem;
    }
}

/* When Streamlit collapses the sidebar, remove its reserved desktop width.
   Keep only the small native reopen control. */
section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    width: 0 !important;
    max-width: 0 !important;
    flex-basis: 0 !important;
    border-right: 0 !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}

/* Some Streamlit versions mark the collapsed state on the sidebar wrapper
   rather than the section itself. Handle that variant as well. */
[data-testid="stSidebar"][data-state="collapsed"] {
    min-width: 0 !important;
    width: 0 !important;
    max-width: 0 !important;
    flex-basis: 0 !important;
    border-right: 0 !important;
}

/* Let the main content reclaim the available width immediately. */
[data-testid="stAppViewContainer"] > .main {
    width: 100% !important;
    max-width: 100% !important;
}

/* Keep the native sidebar reopen button visible and easy to click. */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    left: 0.55rem !important;
    top: 0.75rem !important;
    z-index: 100000 !important;
}


/* Final collapsed-sidebar override.
   Streamlit versions differ in whether collapse is represented by aria-expanded,
   data-state, or an off-screen transform. These selectors ensure the sidebar
   cannot keep the old 360px layout reservation. */
section[data-testid="stSidebar"][aria-expanded="false"],
div[data-testid="stSidebar"][aria-expanded="false"],
section[data-testid="stSidebar"][data-state="collapsed"],
div[data-testid="stSidebar"][data-state="collapsed"] {
    min-width: 0 !important;
    width: 0 !important;
    max-width: 0 !important;
    flex: 0 0 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
}

/* The main app should not retain a sidebar offset after collapse. */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"] {
    max-width: 100% !important;
}

/* On current Streamlit builds the collapsed control is independent of the
   sidebar, so it stays visible even when the sidebar width becomes zero. */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    z-index: 100000 !important;
}

/* ---------- End sidebar visual polish ---------- */

.block-container {max-width: 1500px; padding-top: 1.6rem; padding-bottom: 3rem;}
.dashboard-title {font-size: 2.7rem !important; line-height: 1.05; margin-bottom: .3rem;}
.tiq-context {display:flex; flex-wrap:wrap; gap:.5rem; padding:.7rem .85rem;
 border:1px solid rgba(255,255,255,.10); border-radius:12px;
 background:rgba(255,255,255,.03); margin:.45rem 0 1rem;}
.tiq-chip {padding:.28rem .58rem; border:1px solid rgba(255,255,255,.10);
 border-radius:999px; background:rgba(255,255,255,.04); font-size:.83rem;}
.tiq-section {font-size:.77rem; font-weight:800; letter-spacing:.09em;
 text-transform:uppercase; opacity:.68; margin:1.15rem 0 .5rem;}
.tiq-callout {border:1px solid rgba(255,255,255,.10); border-radius:13px;
 padding:.9rem 1rem; background:rgba(255,255,255,.03); margin:.5rem 0 .9rem;}
.tiq-callout h4 {margin:0 0 .3rem 0;}
.tiq-callout p {margin:.15rem 0; opacity:.88;}
.tiq-strong {border-left:4px solid #36C98F;}
.tiq-watch {border-left:4px solid #EABF55;}
.tiq-action {border-left:4px solid #EF6A6A;}
div[data-testid="stMetric"] {border:1px solid rgba(255,255,255,.10);
 border-radius:13px; padding:.75rem .85rem; background:rgba(255,255,255,.03);}
div[data-testid="stDataFrame"] {border:1px solid rgba(255,255,255,.09); border-radius:12px; overflow:hidden;}
div[data-testid="stExpander"] {border-radius:12px;}
.stButton > button {border-radius:10px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

def tiq_goal_fmt(kpi, value):
    if value is None: return "—"
    if kpi in {"CPA","CPM","CPC"}: return f"${value:,.2f}"
    if kpi == "ROAS": return f"{value:,.2f}x"
    return f"{value:,.2f}%"

def tiq_current(kpi):
    return {
        "CPA": cpa, "ROAS": roas, "Completion Rate": completion_rate,
        "Viewability": campaign_viewability, "CTR": ctr, "CPM": cpm,
        "CPC": cpc, "Conversion Rate": conversion_rate
    }.get(kpi, 0.0)

def tiq_value_fmt(kpi, value):
    return tiq_goal_fmt(kpi, value)

def tiq_status(kpi, actual, goal):
    if goal is None or goal <= 0:
        return "Watch", "Goal unavailable"

    lower_better = kpi in {"CPA", "CPM", "CPC"}
    ratio = actual / goal if goal else 0

    if lower_better:
        # For cost KPIs, lower is better. Signed delta reflects actual-vs-goal;
        # st.metric uses inverse coloring for these metrics.
        if ratio <= 1:
            return "Strong", f"-{(1-ratio)*100:.1f}% vs goal"
        if ratio <= 1.10:
            return "Watch", f"+{(ratio-1)*100:.1f}% vs goal"
        return "Action Needed", f"+{(ratio-1)*100:.1f}% vs goal"

    # For ROAS, Viewability, CTR, Completion Rate and Conversion Rate,
    # higher is better: below target must be negative/red.
    if ratio >= 1:
        return "Strong", f"+{(ratio-1)*100:.1f}% vs goal"
    if ratio >= .90:
        return "Watch", f"-{(1-ratio)*100:.1f}% vs goal"
    return "Action Needed", f"-{(1-ratio)*100:.1f}% vs goal"

def tiq_context_bar():
    sec = f'<span class="tiq-chip">Secondary: {secondary_kpi} {tiq_goal_fmt(secondary_kpi, secondary_kpi_goal)}</span>' if secondary_kpi else ""
    st.markdown(f"""<div class="tiq-context">
    <span class="tiq-chip"><b>{selected_campaign}</b></span>
    <span class="tiq-chip">{funnel_stage} Funnel</span>
    <span class="tiq-chip">{date_range_text}</span>
    <span class="tiq-chip">Primary: {primary_kpi} {tiq_goal_fmt(primary_kpi, primary_kpi_goal)}</span>
    {sec}<span class="tiq-chip">ROAS ≥ {roas_goal:g}x</span>
    </div>""", unsafe_allow_html=True)

def tiq_health():
    goals=[(primary_kpi,primary_kpi_goal)]
    if secondary_kpi: goals.append((secondary_kpi,secondary_kpi_goal))
    goals.append(("ROAS",roas_goal))
    unique=[]; seen=set()
    for x in goals:
        if x[0] not in seen: unique.append(x); seen.add(x[0])
    st.markdown('<div class="tiq-section">Campaign Health</div>', unsafe_allow_html=True)
    cols=st.columns(len(unique))
    for col,(kpi,goal) in zip(cols,unique):
        actual=tiq_current(kpi); status,delta=tiq_status(kpi,actual,goal)
        with col:
            # Streamlit interprets the delta numerically and otherwise colors
            # positive text green. Tell it explicitly whether improvement means
            # increasing or decreasing for this KPI.
            delta_color_mode = "inverse" if kpi in {"CPA", "CPM", "CPC"} else "normal"
            st.metric(
                kpi,
                tiq_value_fmt(kpi, actual),
                delta,
                delta_color=delta_color_mode
            )
            st.caption(f"Goal {tiq_goal_fmt(kpi,goal)} • {status}")
    findings=[]
    for kpi,goal in unique:
        actual=tiq_current(kpi); status,delta=tiq_status(kpi,actual,goal)
        findings.append(({"Action Needed":0,"Watch":1,"Strong":2}[status],status,kpi,actual,goal,delta))
    findings.sort()
    _,status,kpi,actual,goal,delta=findings[0]
    css={"Strong":"tiq-strong","Watch":"tiq-watch","Action Needed":"tiq-action"}[status]
    st.markdown('<div class="tiq-section">What Needs Attention</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="tiq-callout {css}"><h4>{status} — {kpi}</h4>
    <p>Current {tiq_value_fmt(kpi,actual)} vs goal {tiq_goal_fmt(kpi,goal)}. {delta}.</p></div>""",
    unsafe_allow_html=True)

def tiq_period_toolbar(prefix):
    st.markdown('<div class="tiq-section">Optimization Period</div>', unsafe_allow_html=True)
    c1,c2=st.columns([1.35,2.65])
    with c1:
        mode=st.radio("Period",["All Data","Month","Week","Day"],horizontal=True,
                      key=f"{prefix}_pro_period",label_visibility="collapsed")
    d=raw_campaign_df.copy()
    d["Date"]=pd.to_datetime(d["Date"],errors="coerce")
    d=d[d["Date"].notna()].copy()
    with c2:
        if mode=="Month":
            opts=sorted(d["Date"].dt.to_period("M").unique())
            sel=st.selectbox("Month",opts,format_func=lambda p:p.strftime("%B %Y"),
                             key=f"{prefix}_pro_month",label_visibility="collapsed")
            d=d[d["Date"].dt.to_period("M")==sel]
        elif mode=="Week":
            starts=(d["Date"]-pd.to_timedelta(d["Date"].dt.weekday,unit="D")).dt.normalize()
            opts=sorted(starts.unique())
            sel=st.selectbox("Week",opts,format_func=lambda x:f"{pd.Timestamp(x):%b %d} – {(pd.Timestamp(x)+pd.Timedelta(days=6)):%b %d, %Y}",
                             key=f"{prefix}_pro_week",label_visibility="collapsed")
            s=pd.Timestamp(sel); d=d[(d["Date"]>=s)&(d["Date"]<s+pd.Timedelta(days=7))]
        elif mode=="Day":
            opts=sorted(d["Date"].dt.normalize().unique())
            sel=st.selectbox("Day",opts,format_func=lambda x:pd.Timestamp(x).strftime("%B %d, %Y"),
                             key=f"{prefix}_pro_day",label_visibility="collapsed")
            d=d[d["Date"].dt.normalize()==pd.Timestamp(sel)]
        else:
            st.caption("Full campaign reporting period")
    return d

def tiq_opportunity(data, dimension, title):
    if data.empty or dimension not in data.columns: return
    w=data.copy()
    w["Spend_USD"]=pd.to_numeric(w["Spend_USD"],errors="coerce").fillna(0)
    w["Conversions"]=pd.to_numeric(w["Conv_View_Through"],errors="coerce").fillna(0)+pd.to_numeric(w["Conv_Click_Through"],errors="coerce").fillna(0)
    w["Revenue_Attributed_USD"]=pd.to_numeric(w["Revenue_Attributed_USD"],errors="coerce").fillna(0)
    g=w.groupby(dimension,dropna=False).agg(Spend=("Spend_USD","sum"),Conversions=("Conversions","sum"),Revenue=("Revenue_Attributed_USD","sum")).reset_index()
    if g.empty:return
    g["CPA"]=np.where(g["Conversions"]>0,g["Spend"]/g["Conversions"],np.nan)
    g["ROAS"]=np.where(g["Spend"]>0,g["Revenue"]/g["Spend"],0)
    if primary_kpi=="CPA" and g["CPA"].notna().any():
        best=g.loc[g["CPA"].idxmin()]
        reason=f"CPA ${best['CPA']:,.2f} vs ${primary_kpi_goal:,.2f} goal; ROAS {best['ROAS']:.2f}x."
    else:
        best=g.loc[g["ROAS"].idxmax()]
        reason=f"ROAS {best['ROAS']:.2f}x vs {roas_goal:.2f}x goal."
    st.markdown('<div class="tiq-section">Top Opportunity</div>',unsafe_allow_html=True)
    st.markdown(f"""<div class="tiq-callout tiq-strong"><h4>{title}: {best[dimension]}</h4>
    <p>{reason}</p><p><b>Decision:</b> Review for controlled scale while protecting campaign goals.</p></div>""",
    unsafe_allow_html=True)
    with st.expander("Why TradeIQ recommends this"):
        st.write("TradeIQ prioritizes the configured Primary KPI, uses the Secondary KPI as a guardrail, and checks ROAS independently. Validate volume, delivery, and business constraints before making DSP changes.")
        st.dataframe(g.sort_values("CPA" if primary_kpi=="CPA" else "ROAS",
                                  ascending=(primary_kpi=="CPA")).head(10),
                     hide_index=True,use_container_width=True)

def tiq_action_queue():
    st.markdown('<div class="tiq-section">Prioritized Decision Queue</div>',unsafe_allow_html=True)
    goals=[(primary_kpi,primary_kpi_goal)]
    if secondary_kpi: goals.append((secondary_kpi,secondary_kpi_goal))
    goals.append(("ROAS",roas_goal))
    rows=[];seen=set()
    for kpi,goal in goals:
        if kpi in seen: continue
        seen.add(kpi); actual=tiq_current(kpi); status,delta=tiq_status(kpi,actual,goal)
        if status=="Action Needed": priority="High"; action="Diagnose inefficient segments and reduce exposure where evidence supports it."
        elif status=="Watch": priority="Medium"; action="Monitor closely and investigate deterioration before making a large change."
        else: priority="Opportunity"; action="Protect performance and evaluate controlled scaling."
        rows.append({"Priority":priority,"KPI":kpi,"Current":tiq_value_fmt(kpi,actual),
                     "Goal":tiq_goal_fmt(kpi,goal),"Signal":status,"Recommended Action":action})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

def tiq_tracker_template():
    st.markdown('<div class="tiq-section">Optimization Experiment Log</div>',unsafe_allow_html=True)
    st.caption("Track the decision, reason, before/after performance, and outcome.")
    with st.expander("Add / review experiment",expanded=False):
        a,b=st.columns(2)
        with a:
            st.text_input("Optimization",placeholder="Reduced General Interest audience 20%",key="pro_track_action")
            st.text_input("Reason",placeholder="CPA above goal",key="pro_track_reason")
        with b:
            st.text_input("Before",placeholder="CPA $108 | ROAS 1.4x",key="pro_track_before")
            st.text_input("After",placeholder="CPA $82 | ROAS 2.1x",key="pro_track_after")
        st.selectbox("Outcome",["Pending","Positive","Neutral","Negative"],key="pro_track_outcome")

# ---------------------------------------------------
# END PROFESSIONAL UI / UX ENHANCEMENTS
# ---------------------------------------------------

# ---------------------------------------------------
# SECTION 20: PAGE HEADER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    f"""
    <div class="dashboard-subtitle">
        {selected_campaign} &nbsp;•&nbsp;
        {funnel_stage} Funnel &nbsp;•&nbsp;
        {date_range_text}<br>
        Primary KPI: {primary_kpi} ({primary_kpi_goal:g})
        {f"&nbsp;•&nbsp; Secondary KPI: {secondary_kpi} ({secondary_kpi_goal:g})" if secondary_kpi else ""}
        &nbsp;•&nbsp; ROAS Target: {roas_goal:g}
    </div>
    """,
    unsafe_allow_html=True
)

if reconciliation_spend > 0:
    st.warning(
        f"Data reconciliation: {format_currency(reconciliation_spend)} in ghost spend "
        f"is excluded from media performance calculations. "
        f"Open Data Quality / Reconciliation for details."
    )

# ---------------------------------------------------
# END SECTION 20
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 21: CAMPAIGN OVERVIEW PAGE
# ---------------------------------------------------

tiq_context_bar()


# ---------------------------------------------------
# COMPARISON ANALYSIS ENGINE
# ---------------------------------------------------

def _cmp_period_options(data, period_type):
    dates = pd.to_datetime(data["Date"], errors="coerce").dropna()
    if period_type == "Month":
        return sorted(dates.dt.to_period("M").unique())
    if period_type == "Week":
        starts = dates - pd.to_timedelta(dates.dt.weekday, unit="D")
        return sorted(starts.dt.normalize().unique())
    return sorted(dates.dt.normalize().unique())


def _cmp_period_label(value, period_type):
    if period_type == "Month":
        return value.strftime("%b %Y")
    value = pd.Timestamp(value)
    if period_type == "Week":
        return f"{value:%b %d} – {(value + pd.Timedelta(days=6)):%b %d, %Y}"
    return value.strftime("%b %d, %Y")


def _cmp_filter(data, period_type, value):
    d = data.copy()
    d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
    if period_type == "Month":
        return d[d["Date"].dt.to_period("M") == value].copy()
    value = pd.Timestamp(value)
    if period_type == "Week":
        return d[(d["Date"] >= value) & (d["Date"] < value + pd.Timedelta(days=7))].copy()
    return d[d["Date"].dt.normalize() == value.normalize()].copy()


def _cmp_aggregate(data, dimension):
    d = data.copy()
    if dimension not in d.columns:
        return pd.DataFrame()

    for col in ["Spend_USD","Impressions_Served","Impressions_Viewable","Clicks",
                "Conv_View_Through","Conv_Click_Through","Revenue_Attributed_USD"]:
        if col not in d.columns:
            d[col] = 0.0
        d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0)

    d[dimension] = d[dimension].fillna("Not Available").astype(str)
    d = d[~d[dimension].str.strip().str.lower().isin(["", "not available", "none", "nan"])]

    g = d.groupby(dimension, dropna=False).agg(
        Spend=("Spend_USD","sum"),
        Impressions=("Impressions_Served","sum"),
        Viewable_Impressions=("Impressions_Viewable","sum"),
        Clicks=("Clicks","sum"),
        VTC=("Conv_View_Through","sum"),
        CTC=("Conv_Click_Through","sum"),
        Revenue=("Revenue_Attributed_USD","sum")
    ).reset_index()

    g["Conversions"] = g["VTC"] + g["CTC"]
    total_spend = g["Spend"].sum()
    total_conv = g["Conversions"].sum()
    total_rev = g["Revenue"].sum()

    g["Spend Share"] = np.where(total_spend > 0, g["Spend"]/total_spend*100, 0)
    g["Conversion Share"] = np.where(total_conv > 0, g["Conversions"]/total_conv*100, 0)
    g["Revenue Share"] = np.where(total_rev > 0, g["Revenue"]/total_rev*100, 0)
    g["CPM"] = np.where(g["Impressions"]>0, g["Spend"]/g["Impressions"]*1000, np.nan)
    g["CTR"] = np.where(g["Impressions"]>0, g["Clicks"]/g["Impressions"]*100, np.nan)
    g["CPC"] = np.where(g["Clicks"]>0, g["Spend"]/g["Clicks"], np.nan)
    g["CPA"] = np.where(g["Conversions"]>0, g["Spend"]/g["Conversions"], np.nan)
    g["Conversion Rate"] = np.where(g["Clicks"]>0, g["CTC"]/g["Clicks"]*100, np.nan)
    g["ROAS"] = np.where(g["Spend"]>0, g["Revenue"]/g["Spend"], np.nan)
    g["Viewability"] = np.where(g["Impressions"]>0, g["Viewable_Impressions"]/g["Impressions"]*100, np.nan)
    g["Efficiency Index"] = np.where(g["Spend Share"]>0, g["Conversion Share"]/g["Spend Share"], np.nan)
    return g


def _cmp_pct(old, new):
    if pd.isna(old) or pd.isna(new) or old == 0:
        return np.nan
    return (new-old)/abs(old)*100


def _cmp_improvement(kpi, old, new):
    chg = _cmp_pct(old, new)
    if pd.isna(chg):
        return np.nan
    return -chg if kpi in {"CPA","CPM","CPC"} else chg


def _cmp_fmt(kpi, value):
    if pd.isna(value):
        return "—"
    if kpi in {"CPA","CPM","CPC"}:
        return f"${value:,.2f}"
    if kpi == "ROAS":
        return f"{value:.2f}x"
    return f"{value:.2f}%"


def render_comparison_analysis():
    st.markdown('<div class="section-label">Comparison Analysis</div>', unsafe_allow_html=True)
    st.caption("Understand what changed between two periods without clutter.")

    dimensions = {
        "Audience": ("Audience_Segment", "Audience"),
        "Creative": ("Creative_Name", "Creative"),
        "Inventory — Channel": ("Channel", "Channel"),
        "Inventory — Deal Type": ("Deal_Type", "Deal Type"),
        "Inventory — Device Type": ("Device_Type", "Device Type"),
        "Domain / Website": ("Site_Domain", "Domain / Website")
    }

    # One compact setup row.
    s1, s2 = st.columns(2)
    with s1:
        compare_type = st.selectbox("Compare", list(dimensions.keys()), key="cmp_clean_dimension")
    with s2:
        period_type = st.selectbox("Period", ["Month", "Week", "Day"], key="cmp_clean_period")

    dimension, label = dimensions[compare_type]
    if dimension not in raw_campaign_df.columns:
        st.warning(f"{label} is not mapped in this report.")
        return

    useful = raw_campaign_df[dimension].dropna().astype(str).str.strip()
    useful = useful[~useful.str.lower().isin(["", "none", "nan", "not available"])]
    if useful.empty:
        st.warning(f"{label} data is unavailable. Map the corresponding report field first.")
        return

    periods = _cmp_period_options(raw_campaign_df, period_type)
    if len(periods) < 2:
        st.warning(f"At least two {period_type.lower()} periods are required.")
        return

    p1, p2 = st.columns(2)
    with p1:
        period_a = st.selectbox(
            "Period A", periods, index=max(0, len(periods)-2),
            format_func=lambda x: _cmp_period_label(x, period_type),
            key=f"cmp_clean_a_{period_type}"
        )
    with p2:
        period_b = st.selectbox(
            "Period B", periods, index=len(periods)-1,
            format_func=lambda x: _cmp_period_label(x, period_type),
            key=f"cmp_clean_b_{period_type}"
        )

    if period_a == period_b:
        st.warning("Choose two different periods.")
        return

    a = _cmp_aggregate(_cmp_filter(raw_campaign_df, period_type, period_a), dimension)
    b = _cmp_aggregate(_cmp_filter(raw_campaign_df, period_type, period_b), dimension)
    if a.empty or b.empty:
        st.warning("Not enough data is available in one of the selected periods.")
        return

    label_a = _cmp_period_label(period_a, period_type)
    label_b = _cmp_period_label(period_b, period_type)
    c = a.merge(b, on=dimension, how="outer", suffixes=("_A", "_B"))

    for metric0 in ["Spend","Impressions","Clicks","Conversions","Revenue",
                    "Spend Share","Conversion Share","Revenue Share"]:
        for suffix in ["_A","_B"]:
            col = metric0 + suffix
            if col in c.columns:
                c[col] = c[col].fillna(0)

    metric = primary_kpi if primary_kpi in a.columns else "CPA"
    c["Primary Change %"] = c.apply(
        lambda r: _cmp_pct(r.get(f"{metric}_A", np.nan), r.get(f"{metric}_B", np.nan)), axis=1)
    c["Primary Improvement %"] = c.apply(
        lambda r: _cmp_improvement(metric, r.get(f"{metric}_A", np.nan), r.get(f"{metric}_B", np.nan)), axis=1)
    c["Spend Share Change"] = c["Spend Share_B"] - c["Spend Share_A"]
    c["Conversion Share Change"] = c["Conversion Share_B"] - c["Conversion Share_A"]
    c["Efficiency Change %"] = c.apply(
        lambda r: _cmp_pct(r.get("Efficiency Index_A", np.nan), r.get("Efficiency Index_B", np.nan)), axis=1)

    min_spend = max(50.0, float(b["Spend"].sum()) * .01)
    min_imps = 500 if period_type == "Day" else 1000
    min_convs = 2 if period_type == "Day" else 5
    c["Sufficient Volume"] = (
        (c["Spend_B"] >= min_spend) &
        (c["Impressions_B"] >= min_imps) &
        ((c["Conversions_B"] >= min_convs) | (funnel_stage != "Conversion"))
    )

    def classify(r):
        if not r["Sufficient Volume"]:
            return "LOW-VOLUME SIGNAL"
        imp, eff = r["Primary Improvement %"], r["Efficiency Change %"]
        sd, cd = r["Spend Share Change"], r["Conversion Share Change"]
        ei = r.get("Efficiency Index_B", np.nan)
        if pd.notna(imp) and imp >= 10 and pd.notna(eff) and eff >= 5 and cd >= 0:
            return "EMERGING WINNER"
        if pd.notna(imp) and imp <= -10 and pd.notna(eff) and eff <= -10:
            return "DETERIORATING"
        if pd.notna(ei) and ei >= 1.15 and sd <= 1 and cd > sd:
            return "UNDERFUNDED OPPORTUNITY"
        if sd >= 2 and cd < sd and pd.notna(ei) and ei < .90:
            return "OVERFUNDED"
        return "STABLE / WATCH"

    c["Movement"] = c.apply(classify, axis=1)

    # Tabs keep the comparison workspace compact.
    overview, performance, insights = st.tabs(["Overview", "Performance", "Insights"])

    with overview:
        st.markdown(f"### {label_a} → {label_b}")

        counts = c["Movement"].value_counts()
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Winners", int(counts.get("EMERGING WINNER", 0)))
        k2.metric("Deteriorating", int(counts.get("DETERIORATING", 0)))
        k3.metric("Opportunities", int(counts.get("UNDERFUNDED OPPORTUNITY", 0)))
        k4.metric("Low Volume", int(counts.get("LOW-VOLUME SIGNAL", 0)))

        # Top change card.
        ranked = c[c["Sufficient Volume"]].copy()
        if not ranked.empty and ranked["Primary Improvement %"].notna().any():
            best = ranked.loc[ranked["Primary Improvement %"].idxmax()]
            st.markdown('<div class="tiq-section">Biggest Positive Movement</div>', unsafe_allow_html=True)
            st.markdown(
                f"""<div class="tiq-callout tiq-strong">
                <h4>{best[dimension]} — {best['Movement']}</h4>
                <p>{metric}: {_cmp_fmt(metric,best.get(f'{metric}_A',np.nan))}
                → {_cmp_fmt(metric,best.get(f'{metric}_B',np.nan))}
                • Improvement: {best['Primary Improvement %']:+.1f}%</p>
                <p>Spend share change: {best['Spend Share Change']:+.1f} pts •
                Conversion share change: {best['Conversion Share Change']:+.1f} pts</p>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="tiq-section">Performance Movement</div>', unsafe_allow_html=True)
        chart_metric = st.selectbox(
            "Chart Metric",
            list(dict.fromkeys([metric, "ROAS", "Spend", "Viewability", "Efficiency Index"])),
            key="cmp_clean_chart_metric"
        )
        left = f"{chart_metric}_A"
        right = f"{chart_metric}_B"
        if left in c.columns and right in c.columns:
            chart_df = c[[dimension,left,right]].rename(columns={left:label_a,right:label_b})
            long = chart_df.melt(id_vars=dimension,var_name="Period",value_name=chart_metric).dropna()
            chart = alt.Chart(long).mark_bar().encode(
                y=alt.Y(f"{dimension}:N",title=label,sort="-x"),
                x=alt.X(f"{chart_metric}:Q",title=chart_metric),
                yOffset="Period:N",
                color=alt.Color("Period:N",title="Period"),
                tooltip=[
                    alt.Tooltip(f"{dimension}:N",title=label),
                    alt.Tooltip("Period:N"),
                    alt.Tooltip(f"{chart_metric}:Q",format=".2f")
                ]
            ).properties(height=max(300,min(600,len(chart_df)*30)))
            st.altair_chart(chart,use_container_width=True)

    with performance:
        st.markdown('<div class="tiq-section">Comparison Decision Table</div>', unsafe_allow_html=True)
        table_cols = [
            dimension, f"{metric}_A", f"{metric}_B", "Primary Change %",
            "Spend Share_A", "Spend Share_B",
            "Conversion Share_A", "Conversion Share_B",
            "Efficiency Index_A", "Efficiency Index_B", "Movement"
        ]
        table_cols = [x for x in table_cols if x in c.columns]
        st.dataframe(c[table_cols],hide_index=True,use_container_width=True)

        with st.expander("Investment vs Contribution",expanded=False):
            share = pd.concat([
                c[[dimension,"Spend Share_A","Conversion Share_A"]]
                .rename(columns={"Spend Share_A":"Spend Share","Conversion Share_A":"Conversion Share"})
                .assign(Period=label_a),
                c[[dimension,"Spend Share_B","Conversion Share_B"]]
                .rename(columns={"Spend Share_B":"Spend Share","Conversion Share_B":"Conversion Share"})
                .assign(Period=label_b)
            ],ignore_index=True).melt(
                id_vars=[dimension,"Period"],
                value_vars=["Spend Share","Conversion Share"],
                var_name="Share Type",value_name="Share")
            share_chart = alt.Chart(share).mark_bar().encode(
                y=alt.Y(f"{dimension}:N",title=label),
                x=alt.X("Share:Q",title="Share (%)"),
                color=alt.Color("Share Type:N",title=None),
                row=alt.Row("Period:N",title=None),
                tooltip=[alt.Tooltip(f"{dimension}:N",title=label),
                         alt.Tooltip("Period:N"),alt.Tooltip("Share Type:N"),
                         alt.Tooltip("Share:Q",format=".1f")]
            ).properties(height=max(180,min(420,len(c)*24)))
            st.altair_chart(share_chart,use_container_width=True)

        with st.expander("Efficiency Movement",expanded=False):
            e = c[[dimension,"Efficiency Index_A","Efficiency Index_B"]].rename(
                columns={"Efficiency Index_A":label_a,"Efficiency Index_B":label_b})
            el = e.melt(id_vars=dimension,var_name="Period",value_name="Efficiency Index").dropna()
            ec = alt.Chart(el).mark_bar().encode(
                y=alt.Y(f"{dimension}:N",title=label),
                x=alt.X("Efficiency Index:Q",title="Conversion Share ÷ Spend Share"),
                yOffset="Period:N",color=alt.Color("Period:N",title="Period"),
                tooltip=[alt.Tooltip(f"{dimension}:N",title=label),
                         alt.Tooltip("Period:N"),alt.Tooltip("Efficiency Index:Q",format=".2f")]
            ).properties(height=max(300,min(600,len(e)*30)))
            st.altair_chart(ec,use_container_width=True)

        with st.expander("View Detailed Comparison Data",expanded=False):
            st.dataframe(c.drop(columns=["_priority"],errors="ignore"),hide_index=True,use_container_width=True)

    with insights:
        st.markdown('<div class="tiq-section">What Changed?</div>', unsafe_allow_html=True)
        priority={"DETERIORATING":0,"OVERFUNDED":1,"EMERGING WINNER":2,
                  "UNDERFUNDED OPPORTUNITY":3,"STABLE / WATCH":4,"LOW-VOLUME SIGNAL":5}
        q=c.assign(_priority=c["Movement"].map(priority).fillna(9)).sort_values(
            ["_priority","Spend_B"],ascending=[True,False])

        for _,r in q.head(8).iterrows():
            movement=r["Movement"]
            action={
                "EMERGING WINNER":"Evaluate controlled scaling while protecting campaign goals.",
                "DETERIORATING":"Investigate the drivers and consider reducing exposure if deterioration persists.",
                "UNDERFUNDED OPPORTUNITY":"Consider incremental budget because contribution is outpacing investment.",
                "OVERFUNDED":"Review allocation because investment is growing faster than contribution.",
                "LOW-VOLUME SIGNAL":"Gather more data before making a material optimization.",
                "STABLE / WATCH":"Maintain and continue monitoring."
            }[movement]
            css="tiq-strong" if movement in {"EMERGING WINNER","UNDERFUNDED OPPORTUNITY"} else "tiq-action" if movement in {"DETERIORATING","OVERFUNDED"} else "tiq-watch"
            chg=r["Primary Change %"]
            st.markdown(
                f"""<div class="tiq-callout {css}">
                <h4>{r[dimension]} — {movement}</h4>
                <p>{metric}: {_cmp_fmt(metric,r.get(f'{metric}_A',np.nan))}
                → {_cmp_fmt(metric,r.get(f'{metric}_B',np.nan))}
                ({f'{chg:+.1f}%' if pd.notna(chg) else 'N/A'})</p>
                <p>Spend share: {r['Spend Share Change']:+.1f} pts •
                Conversion share: {r['Conversion Share Change']:+.1f} pts •
                Efficiency: {f"{r['Efficiency Change %']:+.1f}%" if pd.notna(r['Efficiency Change %']) else 'N/A'}</p>
                <p><b>Action:</b> {action}</p></div>""",unsafe_allow_html=True)

        with st.expander("Evidence & Classification Logic",expanded=False):
            st.markdown("""
**Emerging Winner** — Primary KPI and efficiency improve while contribution is stable or growing.

**Deteriorating** — Primary KPI and efficiency both weaken materially.

**Underfunded Opportunity** — Contribution exceeds investment and the entity has room to scale.

**Overfunded** — Spend share rises faster than conversion contribution while efficiency is weak.

**Stable / Watch** — No sufficiently strong directional change.

**Low-Volume Signal** — Delivery is too limited for a strong optimization recommendation.

**Efficiency Index = Conversion Share ÷ Spend Share.**
            """)

# ---------------------------------------------------
# END COMPARISON ANALYSIS ENGINE
# ---------------------------------------------------



# ---------------------------------------------------
# CLEAN ANALYZER UX
# ---------------------------------------------------
def _ca_period(prefix):
    d=raw_campaign_df.copy()
    d["Date"]=pd.to_datetime(d["Date"],errors="coerce")
    d=d[d["Date"].notna()].copy()
    c1,c2=st.columns([1,2])
    with c1:
        mode=st.selectbox("Period",["All Data","Month","Week","Day"],key=f"{prefix}_clean_period")
    with c2:
        if mode=="Month":
            opts=sorted(d["Date"].dt.to_period("M").unique())
            v=st.selectbox("Select Month",opts,format_func=lambda x:x.strftime("%B %Y"),key=f"{prefix}_clean_month")
            d=d[d["Date"].dt.to_period("M")==v]
        elif mode=="Week":
            starts=(d["Date"]-pd.to_timedelta(d["Date"].dt.weekday,unit="D")).dt.normalize()
            opts=sorted(starts.unique())
            v=st.selectbox("Select Week",opts,format_func=lambda x:f"{pd.Timestamp(x):%b %d} – {(pd.Timestamp(x)+pd.Timedelta(days=6)):%b %d, %Y}",key=f"{prefix}_clean_week")
            s=pd.Timestamp(v); d=d[(d["Date"]>=s)&(d["Date"]<s+pd.Timedelta(days=7))]
        elif mode=="Day":
            opts=sorted(d["Date"].dt.normalize().unique())
            v=st.selectbox("Select Day",opts,format_func=lambda x:pd.Timestamp(x).strftime("%B %d, %Y"),key=f"{prefix}_clean_day")
            d=d[d["Date"].dt.normalize()==pd.Timestamp(v)]
        else:
            st.caption("Full campaign reporting period")
    return d

def _ca_agg(d,dim):
    d=d.copy()
    if dim not in d.columns:return pd.DataFrame()
    for c in ["Spend_USD","Impressions_Served","Impressions_Viewable","Clicks","Conv_View_Through","Conv_Click_Through","Revenue_Attributed_USD"]:
        if c not in d.columns:d[c]=0.0
        d[c]=pd.to_numeric(d[c],errors="coerce").fillna(0)
    d[dim]=d[dim].fillna("Not Available").astype(str)
    d=d[~d[dim].str.strip().str.lower().isin(["","none","nan","not available"])]
    g=d.groupby(dim,dropna=False).agg(
        Spend=("Spend_USD","sum"),Impressions=("Impressions_Served","sum"),
        Viewable=("Impressions_Viewable","sum"),Clicks=("Clicks","sum"),
        VTC=("Conv_View_Through","sum"),CTC=("Conv_Click_Through","sum"),
        Revenue=("Revenue_Attributed_USD","sum")).reset_index()
    g["Conversions"]=g["VTC"]+g["CTC"]
    ts=g["Spend"].sum();tc=g["Conversions"].sum()
    g["Spend Share"]=np.where(ts>0,g["Spend"]/ts*100,0)
    g["Conversion Share"]=np.where(tc>0,g["Conversions"]/tc*100,0)
    g["CPM"]=np.where(g["Impressions"]>0,g["Spend"]/g["Impressions"]*1000,np.nan)
    g["CTR"]=np.where(g["Impressions"]>0,g["Clicks"]/g["Impressions"]*100,np.nan)
    g["CPC"]=np.where(g["Clicks"]>0,g["Spend"]/g["Clicks"],np.nan)
    g["CPA"]=np.where(g["Conversions"]>0,g["Spend"]/g["Conversions"],np.nan)
    g["Conversion Rate"]=np.where(g["Clicks"]>0,g["CTC"]/g["Clicks"]*100,np.nan)
    g["ROAS"]=np.where(g["Spend"]>0,g["Revenue"]/g["Spend"],np.nan)
    g["Viewability"]=np.where(g["Impressions"]>0,g["Viewable"]/g["Impressions"]*100,np.nan)
    g["Efficiency Index"]=np.where(g["Spend Share"]>0,g["Conversion Share"]/g["Spend Share"],np.nan)
    return g

def _ca_decision(r):
    v=r.get(primary_kpi,np.nan)
    if pd.isna(v) or not primary_kpi_goal:return "WATCH"
    lower=primary_kpi in {"CPA","CPM","CPC"}
    good=v<=primary_kpi_goal if lower else v>=primary_kpi_goal
    bad=v>primary_kpi_goal*1.15 if lower else v<primary_kpi_goal*.85
    rok=pd.isna(r.get("ROAS",np.nan)) or not roas_goal or r["ROAS"]>=roas_goal
    sok=True
    if secondary_kpi and secondary_kpi in r.index and secondary_kpi_goal:
        sv=r.get(secondary_kpi,np.nan)
        if pd.notna(sv):sok=sv<=secondary_kpi_goal if secondary_kpi in {"CPA","CPM","CPC"} else sv>=secondary_kpi_goal
    if good and rok and sok and r.get("Efficiency Index",0)>=1.10:return "SCALE"
    if bad or not rok:return "REDUCE / INVESTIGATE"
    if good and sok:return "MAINTAIN"
    return "WATCH"

def render_clean_analyzer(label,dim,prefix):
    st.markdown(f'<div class="section-label">{label} Analyzer</div>',unsafe_allow_html=True)
    st.caption(f"Focus on the {label.lower()} signals that matter for optimization.")
    if dim not in raw_campaign_df.columns:
        st.warning(f"{label} is not mapped in this report.");return
    useful=raw_campaign_df[dim].dropna().astype(str).str.strip()
    if useful[~useful.str.lower().isin(["","none","nan","not available"])].empty:
        st.warning(f"{label} data is unavailable. Map the corresponding report field first.");return

    g=_ca_agg(_ca_period(prefix),dim)
    if g.empty:st.warning("No usable data exists for the selected period.");return
    g["Decision"]=g.apply(_ca_decision,axis=1)

    spend=g["Spend"].sum();conv=g["Conversions"].sum();rev=g["Revenue"].sum()
    imps=g["Impressions"].sum();clicks=g["Clicks"].sum();view=g["Viewable"].sum()
    summary={"Spend":spend,"CPA":spend/conv if conv else np.nan,"ROAS":rev/spend if spend else np.nan,
             "Viewability":view/imps*100 if imps else np.nan,"CTR":clicks/imps*100 if imps else np.nan,
             "CPM":spend/imps*1000 if imps else np.nan,"CPC":spend/clicks if clicks else np.nan,
             "Conversion Rate":g["CTC"].sum()/clicks*100 if clicks else np.nan}

    overview,performance,insights=st.tabs(["Overview","Performance","Insights"])

    with overview:
        metrics=["Spend",primary_kpi,"ROAS"]
        if secondary_kpi and secondary_kpi not in metrics:metrics.append(secondary_kpi)
        cols=st.columns(len(metrics))
        for col,k in zip(cols,metrics):
            with col:
                val=summary.get(k,np.nan)
                if k=="Spend":st.metric("Spend",f"${val:,.0f}")
                else:
                    goal=primary_kpi_goal if k==primary_kpi else secondary_kpi_goal if secondary_kpi and k==secondary_kpi else roas_goal if k=="ROAS" else None
                    if goal:
                        status,delta=tiq_status(k,val,goal)
                        st.metric(k,tiq_value_fmt(k,val),delta,delta_color="inverse" if k in {"CPA","CPM","CPC"} else "normal")
                        st.caption(f"Goal {tiq_goal_fmt(k,goal)} • {status}")
                    else:st.metric(k,tiq_value_fmt(k,val))

        candidates=g[g["Decision"].isin(["SCALE","MAINTAIN"])]
        if candidates.empty:candidates=g
        if primary_kpi in candidates.columns and candidates[primary_kpi].notna().any():
            best=candidates.loc[candidates[primary_kpi].idxmin()] if primary_kpi in {"CPA","CPM","CPC"} else candidates.loc[candidates[primary_kpi].idxmax()]
        else:best=candidates.loc[candidates["Efficiency Index"].fillna(-1).idxmax()]
        st.markdown('<div class="tiq-section">Top Opportunity</div>',unsafe_allow_html=True)
        st.markdown(f"""<div class="tiq-callout tiq-strong"><h4>{best[dim]} — {best['Decision']}</h4>
        <p>{primary_kpi}: {tiq_value_fmt(primary_kpi,best.get(primary_kpi,np.nan))} • ROAS: {tiq_value_fmt('ROAS',best.get('ROAS',np.nan))} • Efficiency Index: {best.get('Efficiency Index',np.nan):.2f}</p></div>""",unsafe_allow_html=True)

        st.markdown('<div class="tiq-section">Performance Chart</div>',unsafe_allow_html=True)
        metric=st.selectbox("Chart Metric",list(dict.fromkeys([primary_kpi,"ROAS","Spend","Viewability","Efficiency Index"])),key=f"{prefix}_clean_chart")
        cd=g[[dim,metric]].dropna().sort_values(metric,ascending=metric in {"CPA","CPM","CPC"}).head(20)
        chart=alt.Chart(cd).mark_bar().encode(
            y=alt.Y(f"{dim}:N",title=label,sort="-x"),x=alt.X(f"{metric}:Q",title=metric),
            tooltip=[alt.Tooltip(f"{dim}:N",title=label),alt.Tooltip(f"{metric}:Q",format=".2f")]
        ).properties(height=max(300,min(600,len(cd)*30)))
        st.altair_chart(chart,use_container_width=True)

    with performance:
        st.markdown('<div class="tiq-section">Decision Table</div>',unsafe_allow_html=True)
        cols=[dim,"Spend",primary_kpi,"ROAS","Efficiency Index","Decision"]
        if secondary_kpi and secondary_kpi in g.columns and secondary_kpi not in cols:cols.insert(-2,secondary_kpi)
        st.dataframe(g[cols].sort_values(primary_kpi,ascending=primary_kpi in {"CPA","CPM","CPC"}),hide_index=True,use_container_width=True)
        with st.expander("View Detailed Metrics"):
            detail=[dim,"Spend","Spend Share","Impressions","CPM","Clicks","CTR","Conversions","Conversion Share","CPA","ROAS","Viewability","Conversion Rate","Efficiency Index","Decision"]
            st.dataframe(g[[c for c in detail if c in g.columns]],hide_index=True,use_container_width=True)

    with insights:
        st.markdown('<div class="tiq-section">TradeIQ Recommendations</div>',unsafe_allow_html=True)
        order={"REDUCE / INVESTIGATE":0,"SCALE":1,"WATCH":2,"MAINTAIN":3}
        q=g.assign(_priority=g["Decision"].map(order).fillna(9)).sort_values(["_priority","Spend"],ascending=[True,False])
        for _,r in q.head(8).iterrows():
            dec=r["Decision"]
            css="tiq-strong" if dec=="SCALE" else "tiq-action" if dec=="REDUCE / INVESTIGATE" else "tiq-watch"
            action={"SCALE":"Evaluate incremental scale while protecting campaign goals.",
                    "REDUCE / INVESTIGATE":"Investigate performance drivers and consider reducing exposure.",
                    "WATCH":"Keep allocation stable and monitor for a clearer signal.",
                    "MAINTAIN":"Maintain current allocation unless priorities change."}[dec]
            st.markdown(f"""<div class="tiq-callout {css}"><h4>{r[dim]} — {dec}</h4>
            <p>{primary_kpi}: {tiq_value_fmt(primary_kpi,r.get(primary_kpi,np.nan))} • ROAS: {tiq_value_fmt('ROAS',r.get('ROAS',np.nan))} • Spend Share: {r.get('Spend Share',0):.1f}% • Conversion Share: {r.get('Conversion Share',0):.1f}%</p>
            <p><b>Action:</b> {action}</p></div>""",unsafe_allow_html=True)
        with st.expander("Evidence & Decision Logic"):
            st.markdown(f"""TradeIQ prioritizes **{primary_kpi}** as the decision KPI.
{f'**{secondary_kpi}** is used as a quality guardrail.' if secondary_kpi else ''}
**ROAS** is evaluated independently. **Efficiency Index = Conversion Share ÷ Spend Share.**""")
# ---------------------------------------------------
# END CLEAN ANALYZER UX
# ---------------------------------------------------


# ---------------------------------------------------
# PACING & DELIVERY: FLIGHT CALCULATION AND EVIDENCE
# ---------------------------------------------------
def calculate_flight_pacing(start, end, report_through, spend_to_date, total_budget):
    start, end, report_through = [pd.Timestamp(x).normalize() for x in (start, end, report_through)]
    if end < start or total_budget <= 0:
        raise ValueError('End date must follow start date and budget must be positive.')
    total_days = (end - start).days + 1
    elapsed = max(0, min(total_days, (report_through - start).days + 1))
    expected = elapsed / total_days * 100
    actual = spend_to_date / total_budget * 100
    gap = round(actual - expected, 10)
    remaining_days = total_days - elapsed
    remaining_budget = max(0, total_budget - spend_to_date)
    status = 'Not Started' if elapsed == 0 else ('Underpacing' if gap < -5 else 'Overpacing' if gap > 5 else 'On Track')
    return dict(total_days=total_days, elapsed=elapsed, expected=expected, actual=actual,
                gap=gap, remaining_days=remaining_days, remaining_budget=remaining_budget,
                required_daily=remaining_budget / remaining_days if remaining_days else None, status=status)


def render_pacing_delivery_analyzer():
    st.subheader('Pacing & Delivery Analyzer')
    st.caption('Compare spend to elapsed flight time, then investigate the delivery pattern.')
    source = campaign_df.copy()
    source['Date'] = pd.to_datetime(source['Date'], errors='coerce').dt.normalize()
    dates = source['Date'].dropna()
    if dates.empty:
        st.info('A valid mapped Date column is required for pacing analysis.')
        return
    # Report cutoff comes from all campaign rows, including reconciliation rows.
    raw_dates = pd.to_datetime(raw_campaign_df['Date'], errors='coerce').dropna()
    cutoff = raw_dates.max().normalize() if not raw_dates.empty else dates.max()
    key = 'pacing_' + str(selected_campaign)
    st.markdown('### Campaign Flight Setup')
    c1, c2, c3 = st.columns(3)
    start = c1.date_input('Campaign Start Date', dates.min().date(), key=key+'_start')
    end = c2.date_input('Campaign End Date', dates.max().date(), key=key+'_end')
    flight_budget = c3.number_input('Total Flight Budget ($)', min_value=0.0, value=float(max(0, budget)), key=key+'_budget', help='Confirm the full campaign budget. Repeated campaign budgets in line-item rows must not be summed.')
    st.caption(f'Current report through: {cutoff:%b %d, %Y}. Dates are inclusive; expected spend follows an even daily schedule. Initial dates are report dates—set the planned flight dates.')
    complete = st.checkbox('I confirm the report includes all spend from flight start through the report cutoff', key=key+'_complete')
    if end < start or flight_budget <= 0:
        st.info('Set a valid flight and a positive total budget to continue.')
        return
    first, last = pd.Timestamp(start), pd.Timestamp(end)
    flight = source[source['Date'].between(first, min(last, cutoff))].copy()
    flight_spend = float(flight['Spend_USD'].sum())
    p = calculate_flight_pacing(start, end, cutoff, flight_spend, flight_budget)
    if not complete:
        st.warning('Provisional: spend coverage is unconfirmed. Delivery status and actions require complete flight-to-date spend.')
    st.markdown('### Delivery Health')
    title = f"{p['status']} — {p['gap']:+.1f}pp vs expected delivery"
    if not complete:
        title = 'Provisional • ' + title
    (st.warning if p['status'] in ('Underpacing', 'Overpacing') else st.info)(title)
    tiles = st.columns(4)
    for col, label, value in zip(tiles, ['Flight Progress', 'Actual Spend', 'Expected Spend', 'Pacing Gap'], [f"{p['expected']:.1f}%", f"{p['actual']:.1f}%", f"{p['expected']:.1f}%", f"{p['gap']:+.1f}pp"]):
        col.metric(label, value)
    st.caption(f"Spend to date: ${flight_spend:,.2f} / ${flight_budget:,.2f} • {p['elapsed']} of {p['total_days']} flight days elapsed • ±5pp tolerance")
    if cutoff < first:
        st.info('The report predates the flight. No delivery assessment is available yet.')
        return
    if flight.empty:
        st.warning('No valid media rows are available within this flight. Check dates and reconciliation before changing delivery.')
        return
    # Calendar windows include non-spending dates, avoiding active-day bias.
    through = min(last, cutoff)
    daily = flight.groupby('Date')[['Spend_USD', 'Impressions_Served']].sum().reindex(pd.date_range(first, through), fill_value=0)
    recent = daily.tail(3)
    previous = daily.iloc[max(0, len(daily)-10):max(0, len(daily)-3)]
    observed_dates = set(flight['Date'].dropna())
    missing_days = sum(day not in observed_dates for day in daily.index)
    recent_avg = float(recent['Spend_USD'].mean())
    evidence, findings, actions = [], [], []
    evidence.append(f"Recent daily spend: ${recent_avg:,.2f} across {len(recent)} calendar days.")
    required = p['required_daily']
    if required is not None:
        evidence.append(f"Required daily spend: ${required:,.2f} over {p['remaining_days']} remaining days; remaining budget ${p['remaining_budget']:,.2f}.")
        if required > 0 and len(recent) == 3:
            velocity = recent_avg / required
            if velocity < .8:
                findings.append(('Low recent spend velocity', f'Recent daily spend is {(1-velocity)*100:.1f}% below the rate needed to finish on budget. This measures the shortfall; it does not establish a bid or targeting cause.'))
                actions.append('Review daily caps, bid competitiveness, eligible audience size, frequency limits, and deal availability in the DSP before increasing allocation.')
            elif velocity > 1.2:
                findings.append(('High recent spend velocity', f'Recent daily spend is {(velocity-1)*100:.1f}% above the remaining-budget daily rate.'))
                actions.append('Review daily pacing controls and caps; align planned daily spend with the remaining flight budget.')
    if len(previous) >= 3 and len(recent) == 3:
        old_spend, new_spend = previous['Spend_USD'].mean(), recent['Spend_USD'].mean()
        old_imp, new_imp = previous['Impressions_Served'].mean(), recent['Impressions_Served'].mean()
        spend_change = new_spend / old_spend - 1 if old_spend > 0 else None
        imp_change = new_imp / old_imp - 1 if old_imp > 0 else None
        old_cpm = previous['Spend_USD'].sum() / previous['Impressions_Served'].sum() * 1000 if previous['Impressions_Served'].sum() > 0 else None
        new_cpm = recent['Spend_USD'].sum() / recent['Impressions_Served'].sum() * 1000 if recent['Impressions_Served'].sum() > 0 else None
        cpm_change = new_cpm / old_cpm - 1 if old_cpm and new_cpm is not None else None
        if spend_change is not None:
            evidence.append(f"Daily spend change: {spend_change:+.1%}; last 3 calendar days vs previous {len(previous)} calendar days.")
        if imp_change is not None:
            evidence.append(f'Daily impression change: {imp_change:+.1%}.')
        if cpm_change is not None:
            evidence.append(f'Weighted CPM: ${old_cpm:,.2f} → ${new_cpm:,.2f} ({cpm_change:+.1%}).')
        if spend_change is not None and spend_change > .25:
            findings.append(('Recent spend acceleration', 'Daily spend rose more than 25% against the preceding calendar window. Check DSP settings and change history to identify the trigger.'))
        if imp_change is not None and imp_change < -.2 and cpm_change is not None and abs(cpm_change) <= .1:
            findings.append(('Falling delivered scale', 'Daily impressions declined more than 20% while weighted CPM stayed within 10%. Limited eligible supply is a hypothesis; delivered impressions do not measure auction opportunity.'))
        if cpm_change is not None and cpm_change > .2:
            findings.append(('Rising media cost', 'Weighted CPM increased more than 20%. This explains fewer impressions per dollar, but alone does not explain an inability to spend.'))
        if cpm_change is not None and cpm_change < -.2 and imp_change is not None and imp_change > .25:
            findings.append(('Cheaper, higher-volume delivery', 'CPM fell more than 20% while daily impressions rose more than 25%. Review inventory mix before changing bids.'))
    line_spend = flight.groupby('Line_Item_Name')['Spend_USD'].sum().sort_values(ascending=False)
    if len(line_spend) >= 3 and flight_spend > 0:
        top_share = float(line_spend.iloc[:2].sum() / flight_spend)
        evidence.append(f'Top two reported line items account for {top_share:.1%} of flight-to-date spend across {len(line_spend)} reported line items.')
        if top_share > .8:
            findings.append(('Concentrated delivery', 'More than 80% of spend is in two reported line items. This may be intentional; confirm planned allocations and eligibility before redistributing.'))
            actions.append('Inspect low-spending reported line items and their planned budgets; move budget only where KPI guardrails permit.')
    if missing_days:
        evidence.append(f'{missing_days} calendar dates have no valid media rows. These can represent no delivery or omitted report data; no-row dates are treated as zero only for the provisional trend.')
    if reconciliation_spend > 0:
        evidence.append(f'Campaign reconciliation includes ${reconciliation_spend:,.2f} excluded spend. This analyzer uses valid media spend; reconcile billed delivery separately.')
    st.markdown('### Why Is This Happening?')
    if not complete:
        st.info('Cause assessment is provisional until spend coverage is confirmed.')
    if findings:
        for label, detail in findings[:2]:
            st.markdown(f'**{label}**  \n{detail}')
    else:
        st.info('No clear driver is established by the available report. Review DSP settings and data coverage.' if p['status'] != 'On Track' else 'Delivery is within tolerance. Available evidence does not establish a near-term delivery risk.')
    if p['remaining_days'] == 0:
        st.caption('Flight completed: this is a final delivery assessment. There are no remaining days to recover or slow delivery.')
    elif complete and len(recent) == 3:
        forecast = flight_spend + recent_avg * p['remaining_days']
        st.caption(f'At the last 3 calendar days’ spend rate, projected final delivery is {forecast / flight_budget:.1%}. This is a constant-rate scenario, not a guaranteed forecast.')
    st.markdown('### Recommended Action')
    if not complete:
        st.write('Confirm the full flight-to-date export and total budget before taking a pacing action.')
    elif p['remaining_days'] == 0:
        st.write('Reconcile final delivery against the flight budget and document the gap for the next flight.')
    else:
        if not actions:
            actions = ['Maintain current delivery controls and monitor daily spend against the remaining-budget rate.' if p['status'] == 'On Track' else 'Verify report coverage and review DSP daily budgets, bids, targeting, and supply availability. Cause is not confirmed.']
        for i, action in enumerate(actions[:2], 1):
            st.write(f'{i}. {action}')
        st.caption('Recheck after 1–3 complete reporting days. Protect configured performance goals when adjusting delivery.')
    with st.expander('View Supporting Evidence', expanded=False):
        st.caption('Diagnostic thresholds are initial heuristics, not statistically confirmed anomalies or causal proof.')
        for item in evidence:
            st.write('• ' + item)
        st.caption('Trend comparison requires 3 recent and at least 3 prior calendar days. Missing rows are not proof of inactivity; line items absent from the report cannot be diagnosed.')
        trend = daily.copy()
        trend['Actual Cumulative Spend'] = trend['Spend_USD'].cumsum()
        trend['Expected Cumulative Spend'] = np.arange(1, len(trend)+1) / p['total_days'] * flight_budget
        st.line_chart(trend[['Actual Cumulative Spend', 'Expected Cumulative Spend']])
        st.dataframe(daily.reset_index().rename(columns={'index':'Date'}), hide_index=True, use_container_width=True)
# ---------------------------------------------------
# END PACING & DELIVERY ANALYZER
# ---------------------------------------------------


if page == "Campaign Overview": 
    tiq_health()


    # ---------------------------------------------------
    # CAMPAIGN HEALTH + KEY INSIGHTS
    # ---------------------------------------------------
    # These panels remain side by side on larger screens.
    # Streamlit automatically stacks the columns on smaller
    # screens, while the content inside each panel also scales.

    health_panel, insights_panel = st.columns(
        [0.90, 1.45],
        gap="large"
    )


    # ---------------------------------------------------
    # LEFT PANEL: CAMPAIGN HEALTH
    # ---------------------------------------------------

    with health_panel:

        st.markdown(
            '<div class="section-label">Campaign Health</div>',
            unsafe_allow_html=True
        )


        if funnel_stage == "Conversion":

            delivery_state = (
                "good"
                if delivery_status == "On Track"
                else (
                    "bad"
                    if delivery_status == "Over-Delivering"
                    else "warn"
                )
            )

            render_health_card(
                "Delivery",
                delivery_status,
                delivery_state
            )

            render_health_card(
                "CPA Efficiency",
                cpa_status,
                "good" if cpa <= cpa_target else "bad"
            )

            render_health_card(
                "ROAS",
                roas_status,
                "good" if roas >= roas_target else "bad"
            )


        elif funnel_stage == "Awareness":

            delivery_state = (
                "good"
                if delivery_status == "On Track"
                else (
                    "bad"
                    if delivery_status == "Over-Delivering"
                    else "warn"
                )
            )

            render_health_card(
                "Delivery",
                delivery_status,
                delivery_state
            )

            render_health_card(
                "Completion Rate",
                completion_rate_status,
                (
                    "good"
                    if completion_rate >= completion_rate_target
                    else "warn"
                )
            )


    # ---------------------------------------------------
    # RIGHT PANEL: KEY INSIGHTS
    # ---------------------------------------------------

    with insights_panel:

        st.markdown(
            '<div class="section-label">Key Insights</div>',
            unsafe_allow_html=True
        )


        insight_items = []


        # Delivery insight

        if delivery_status == "On Track":

            insight_items.append(
                (
                    "green",
                    f"Campaign delivery is on track at "
                    f"{delivery_percent:.2f}% of budget."
                )
            )

        elif delivery_status == "Under-Delivering":

            insight_items.append(
                (
                    "yellow",
                    f"Campaign is under-delivering at "
                    f"{delivery_percent:.2f}% of budget and may need "
                    f"additional scale or pacing review."
                )
            )

        else:

            insight_items.append(
                (
                    "red",
                    f"Campaign is over-delivering at "
                    f"{delivery_percent:.2f}% of budget and should be "
                    f"reviewed for budget control."
                )
            )


        # Conversion-specific insights

        if funnel_stage == "Conversion":

            if cpa <= cpa_target:

                insight_items.append(
                    (
                        "green",
                        f"CPA is efficient at ${cpa:.2f}, which is below "
                        f"the ${cpa_target:.2f} target."
                    )
                )

            else:

                cpa_gap_percent = (
                    (cpa - cpa_target)
                    / cpa_target
                ) * 100

                cpa_color = (
                    "yellow"
                    if cpa_gap_percent <= 10
                    else "red"
                )

                insight_items.append(
                    (
                        cpa_color,
                        f"CPA is ${cpa:.2f}, which is "
                        f"{cpa_gap_percent:.1f}% above the "
                        f"${cpa_target:.2f} target."
                    )
                )


            if roas >= roas_target:

                insight_items.append(
                    (
                        "green",
                        f"ROAS is strong at {roas:.2f}x versus the "
                        f"{roas_target:.2f}x target."
                    )
                )

            else:

                roas_gap_percent = (
                    (roas_target - roas)
                    / roas_target
                ) * 100

                roas_color = (
                    "yellow"
                    if roas_gap_percent <= 10
                    else "red"
                )

                insight_items.append(
                    (
                        roas_color,
                        f"ROAS is {roas:.2f}x, which is "
                        f"{roas_gap_percent:.1f}% below the "
                        f"{roas_target:.2f}x target."
                    )
                )


        # Awareness-specific insights

        elif funnel_stage == "Awareness":

            completion_gap = (
                completion_rate
                - completion_rate_target
            )

            if completion_rate >= completion_rate_target:

                insight_items.append(
                    (
                        "green",
                        f"Completion Rate is {completion_rate:.2f}%, "
                        f"which is {completion_gap:.2f} percentage points "
                        f"above the {completion_rate_target:.2f}% target."
                    )
                )

            elif completion_rate >= (
                completion_rate_target - 5
            ):

                insight_items.append(
                    (
                        "yellow",
                        f"Completion Rate is {completion_rate:.2f}%, "
                        f"slightly below the {completion_rate_target:.2f}% "
                        f"target."
                    )
                )

            else:

                insight_items.append(
                    (
                        "red",
                        f"Completion Rate is {completion_rate:.2f}%, "
                        f"well below the {completion_rate_target:.2f}% "
                        f"target."
                    )
                )


            insight_items.append(
                (
                    "yellow",
                    f"Current CPM is ${cpm:.2f}. A campaign-specific CPM "
                    f"benchmark has not been configured yet."
                )
            )


        else:

            insight_items.append(
                (
                    "yellow",
                    "Campaign funnel stage has not yet been assigned."
                )
            )


        insight_html = '<div class="insight-box"><ul class="insight-list">'

        for insight_color, insight_text in insight_items:

            insight_html += (
                f'<li class="insight-{insight_color}">'
                f'{insight_text}'
                f'</li>'
            )

        insight_html += '</ul></div>'


        st.markdown(
            insight_html,
            unsafe_allow_html=True
        )


    st.write("")


    # ---------------------------------------------------
    # DELIVERY OVERVIEW
    # ---------------------------------------------------

    st.markdown(
        '<div class="section-label">Delivery Overview</div>',
        unsafe_allow_html=True
    )

    render_tile_grid(
        [
            {
                "label": "Spend",
                "value": format_currency(spend)
            },
            {
                "label": "Budget",
                "value": format_currency(budget)
            },
            {
                "label": "Budget Delivery",
                "value": format_percent(delivery_percent)
            }
        ]
    )


    st.write("")


    # ---------------------------------------------------
    # PERFORMANCE OVERVIEW
    # ---------------------------------------------------

    st.markdown(
        '<div class="section-label">Performance Overview</div>',
        unsafe_allow_html=True
    )


    if funnel_stage == "Awareness":

        render_tile_grid(
            [
                {
                    "label": "Impressions",
                    "value": format_compact_number(impressions)
                },
                {
                    "label": "CPM",
                    "value": format_currency(cpm)
                },
                {
                    "label": "Completion Rate",
                    "value": format_percent(completion_rate),
                    "note": f"Target: {completion_rate_target:.2f}%"
                },
                {
                    "label": "Clicks",
                    "value": format_compact_number(clicks)
                },
                {
                    "label": "CTR",
                    "value": format_percent(ctr)
                },
                {
                    "label": "CPC",
                    "value": format_currency(cpc)
                }
            ]
        )


    elif funnel_stage == "Conversion":

        render_tile_grid(
            [
                {
                    "label": "Total Conversions",
                    "value": format_compact_number(total_conversions)
                },
                {
                    "label": "CPA",
                    "value": format_currency(cpa),
                    "note": f"Target: ${cpa_target:.2f}"
                },
                {
                    "label": "ROAS",
                    "value": format_multiplier(roas),
                    "note": f"Target: {roas_target:.2f}x"
                },
                {
                    "label": "Impressions",
                    "value": format_compact_number(impressions)
                },
                {
                    "label": "CTR",
                    "value": format_percent(ctr)
                },
                {
                    "label": "CPC",
                    "value": format_currency(cpc)
                },
                {
                    "label": "Click-Through Conversions",
                    "value": format_compact_number(click_conversions)
                },
                {
                    "label": "View-Through Conversions",
                    "value": format_compact_number(view_conversions)
                },
                {
                    "label": "Attributed Revenue",
                    "value": format_currency(revenue)
                }
            ]
        )

# ---------------------------------------------------
# END SECTION 21
# ---------------------------------------------------

# ---------------------------------------------------
# SECTION 22: MONTHLY TRENDS PAGE
# ---------------------------------------------------

elif page == "Comparison Analysis":
    render_comparison_analysis()


elif page == "Data Quality / Reconciliation":

    st.markdown(
        '<div class="section-label">Data Quality & Reconciliation</div>',
        unsafe_allow_html=True
    )
    st.caption(
        "TradeIQ validates the raw DSP report before analysis. Hard exclusions are "
        "kept in reconciliation records and are not included in performance metrics. "
        "Warnings remain in analysis until reviewed."
    )

    render_tile_grid(
        [
            {
                "label": "Reported Spend",
                "value": format_currency(reported_spend),
                "note": "Raw report total"
            },
            {
                "label": "Valid Media Spend",
                "value": format_currency(valid_media_spend),
                "note": "Used by TradeIQ analyzers"
            },
            {
                "label": "Reconciliation Spend",
                "value": format_currency(reconciliation_spend),
                "note": "Excluded from media spend"
            },
            {
                "label": "Quality Issues",
                "value": format_compact_number(data_quality_issue_count, decimals=0),
                "note": f"{len(reconciliation_df)} exclusions • {len(quality_warning_df)} warnings"
            }
        ],
        compact=True
    )

    st.markdown("### Reconciliation Required")
    st.caption(
        "Current hard-exclusion rule: Spend > 0 with zero impressions is classified "
        "as Ghost Spend and excluded from all media-performance calculations."
    )

    if reconciliation_df.empty:
        st.success("No reconciliation exclusions were detected for this campaign.")
    else:
        reconciliation_columns = [
            column for column in [
                "Source_Row", "Date", "Campaign_Name", "Line_Item_Name",
                "Spend_USD", "Impressions_Served", "Data_Quality_Status",
                "Reconciliation_Reason"
            ] if column in reconciliation_df.columns
        ]
        reconciliation_display = reconciliation_df[reconciliation_columns].copy()
        if "Date" in reconciliation_display.columns:
            reconciliation_display["Date"] = pd.to_datetime(
                reconciliation_display["Date"], errors="coerce"
            ).dt.strftime("%b %d, %Y")
        if "Spend_USD" in reconciliation_display.columns:
            reconciliation_display["Spend_USD"] = reconciliation_display["Spend_USD"].apply(
                format_currency
            )
        st.dataframe(
            reconciliation_display,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### Data Quality Warnings")
    st.caption(
        "Warnings are surfaced for investigation but remain in the analytical dataset "
        "because unusual delivery can still be legitimate."
    )

    if quality_warning_df.empty:
        st.success("No additional data-quality warnings were detected for this campaign.")
    else:
        warning_columns = [
            column for column in [
                "Source_Row", "Date", "Campaign_Name", "Line_Item_Name",
                "Spend_USD", "Impressions_Served", "Clicks",
                "Conv_View_Through", "Conv_Click_Through",
                "Revenue_Attributed_USD", "Reconciliation_Reason"
            ] if column in quality_warning_df.columns
        ]
        warning_display = quality_warning_df[warning_columns].copy()
        if "Date" in warning_display.columns:
            warning_display["Date"] = pd.to_datetime(
                warning_display["Date"], errors="coerce"
            ).dt.strftime("%b %d, %Y")
        for money_column in ["Spend_USD", "Revenue_Attributed_USD"]:
            if money_column in warning_display.columns:
                warning_display[money_column] = warning_display[money_column].apply(
                    format_currency
                )
        st.dataframe(
            warning_display,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### Reconciliation Rulebook")
    rulebook = pd.DataFrame([
        {
            "Rule": "Spend > 0 and Impressions = 0",
            "Classification": "Reconciliation Required",
            "Treatment": "Exclude from media spend and all downstream analysis",
            "Purpose": "Ghost spend investigation"
        },
        {
            "Rule": "Impressions > 0 and Spend = 0",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate",
            "Purpose": "Validate zero-cost delivery"
        },
        {
            "Rule": "Clicks > Impressions",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate",
            "Purpose": "Data integrity check"
        },
        {
            "Rule": "Conversions > 0 and Impressions = 0",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate",
            "Purpose": "Attribution check"
        },
        {
            "Rule": "Revenue > 0 and Conversions = 0",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate",
            "Purpose": "Measurement mapping check"
        },
        {
            "Rule": "Negative delivery/financial value",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate",
            "Purpose": "Reconciliation/data integrity check"
        },
        {
            "Rule": "Potential exact duplicate",
            "Classification": "Warning",
            "Treatment": "Keep in analysis; investigate before deduplication",
            "Purpose": "Avoid deleting legitimate dimensional rows"
        }
    ])
    st.dataframe(rulebook, use_container_width=True, hide_index=True)


elif page == "Monthly Trends":

    st.markdown(
        '<div class="section-label">Monthly Performance Trends</div>',
        unsafe_allow_html=True
    )


    # ---------------------------------------------------
    # MONTHLY METRIC SELECTOR
    # ---------------------------------------------------

    if funnel_stage == "Awareness":

        monthly_metric_options = {
            "Spend": "Spend",
            "Impressions": "Impressions",
            "CPM": "CPM",
            "Clicks": "Clicks",
            "CTR": "CTR",
            "CPC": "CPC",
            "Completion Rate": "Completion_Rate"
        }

    elif funnel_stage == "Conversion":

        monthly_metric_options = {
            "Spend": "Spend",
            "Impressions": "Impressions",
            "Clicks": "Clicks",
            "CPM": "CPM",
            "CTR": "CTR",
            "CPC": "CPC",
            "Total Conversions": "Total Conversions",
            "CPA": "CPA",
            "Conversion Rate": "Conversion Rate",
            "Revenue": "Revenue",
            "ROAS": "ROAS"
        }

    else:

        monthly_metric_options = {
            "Spend": "Spend"
        }


    selected_trend_metric = st.selectbox(
        "Trend Metric",
        list(monthly_metric_options.keys())
    )

    selected_trend_column = monthly_metric_options[
        selected_trend_metric
    ]


    # ---------------------------------------------------
    # MONTHLY TREND SUMMARY TILES
    # ---------------------------------------------------

    if len(monthly_summary) >= 1:

        latest_month_row = monthly_summary.iloc[-1]

        latest_month_name = latest_month_row["Month"]

        latest_metric_value = latest_month_row[
            selected_trend_column
        ]


        highest_month_index = monthly_summary[
            selected_trend_column
        ].idxmax()

        lowest_month_index = monthly_summary[
            selected_trend_column
        ].idxmin()


        highest_month_name = monthly_summary.loc[
            highest_month_index,
            "Month"
        ]

        highest_metric_value = monthly_summary.loc[
            highest_month_index,
            selected_trend_column
        ]


        lowest_month_name = monthly_summary.loc[
            lowest_month_index,
            "Month"
        ]

        lowest_metric_value = monthly_summary.loc[
            lowest_month_index,
            selected_trend_column
        ]


        if len(monthly_summary) >= 2:

            previous_month_row = monthly_summary.iloc[-2]

            previous_month_name = previous_month_row["Month"]

            previous_metric_value = previous_month_row[
                selected_trend_column
            ]

            absolute_change = (
                latest_metric_value
                - previous_metric_value
            )

            if previous_metric_value != 0:

                mom_change_percent = (
                    absolute_change
                    / abs(previous_metric_value)
                ) * 100

                mom_note = (
                    f"{mom_change_percent:+.2f}% vs "
                    f"{previous_month_name}"
                )

            else:

                mom_change_percent = None

                mom_note = "Previous month = 0"

            mom_value = format_monthly_metric_value(
                selected_trend_metric,
                absolute_change
            )

        else:

            previous_month_name = None
            previous_metric_value = None
            mom_change_percent = None
            mom_note = None
            mom_value = "N/A"


        render_tile_grid(
            [
                {
                    "label": f"Latest ({latest_month_name})",
                    "value": format_monthly_metric_value(
                        selected_trend_metric,
                        latest_metric_value
                    )
                },
                {
                    "label": "Month-over-Month",
                    "value": mom_value,
                    "note": mom_note
                },
                {
                    "label": f"Highest ({highest_month_name})",
                    "value": format_monthly_metric_value(
                        selected_trend_metric,
                        highest_metric_value
                    )
                },
                {
                    "label": f"Lowest ({lowest_month_name})",
                    "value": format_monthly_metric_value(
                        selected_trend_metric,
                        lowest_metric_value
                    )
                }
            ],
            compact=True
        )


    st.write("")


    # ---------------------------------------------------
    # MONTHLY TREND CHART
    # ---------------------------------------------------

    monthly_chart_data = monthly_summary[
        [
            "Month",
            selected_trend_column
        ]
    ].copy()

    month_order = monthly_summary[
        "Month"
    ].tolist()


    monthly_chart = (
        alt.Chart(monthly_chart_data)
        .mark_line(
            point=True
        )
        .encode(
            x=alt.X(
                "Month:N",
                sort=month_order,
                title="Month",
                axis=alt.Axis(
                    labelAngle=0
                )
            ),
            y=alt.Y(
                f"{selected_trend_column}:Q",
                title=selected_trend_metric
            ),
            tooltip=[
                alt.Tooltip(
                    "Month:N",
                    title="Month"
                ),
                alt.Tooltip(
                    f"{selected_trend_column}:Q",
                    title=selected_trend_metric,
                    format=",.2f"
                )
            ]
        )
        .properties(
            height=420
        )
        .interactive()
    )


    st.altair_chart(
        monthly_chart,
        use_container_width=True
    )


    # ---------------------------------------------------
    # MONTHLY TREND INTERPRETATION
    # ---------------------------------------------------

    if len(monthly_summary) >= 2:

        previous_month_row = monthly_summary.iloc[-2]

        previous_month_name = previous_month_row["Month"]

        previous_metric_value = previous_month_row[
            selected_trend_column
        ]


        if latest_metric_value > previous_metric_value:
            direction = "increased"

        elif latest_metric_value < previous_metric_value:
            direction = "decreased"

        else:
            direction = "was unchanged"


        if previous_metric_value != 0:

            mom_change_percent = (
                (
                    latest_metric_value
                    - previous_metric_value
                )
                / abs(previous_metric_value)
            ) * 100

            summary_text = (
                f"{selected_trend_metric} {direction} "
                f"{abs(mom_change_percent):.2f}% from "
                f"{previous_month_name} to {latest_month_name}."
            )

        else:

            summary_text = (
                f"{selected_trend_metric} {direction} from "
                f"{previous_month_name} to {latest_month_name}."
            )


        if selected_trend_metric == "CPA":

            if latest_metric_value < previous_metric_value:
                summary_text += (
                    " Lower CPA indicates improved cost efficiency."
                )
            elif latest_metric_value > previous_metric_value:
                summary_text += (
                    " Higher CPA indicates weaker cost efficiency."
                )


        elif selected_trend_metric == "ROAS":

            if latest_metric_value > previous_metric_value:
                summary_text += (
                    " Higher ROAS indicates stronger return on ad spend."
                )
            elif latest_metric_value < previous_metric_value:
                summary_text += (
                    " Lower ROAS indicates weaker return on ad spend."
                )


        elif selected_trend_metric == "Completion Rate":

            if latest_metric_value > previous_metric_value:
                summary_text += (
                    " Completion Rate improved versus the previous month."
                )
            elif latest_metric_value < previous_metric_value:
                summary_text += (
                    " Completion Rate declined versus the previous month."
                )


        st.info(
            summary_text
        )


    # ---------------------------------------------------
    # MONTHLY DATA TABLE
    # ---------------------------------------------------

    with st.expander(
        "View Monthly Performance Data"
    ):

        if funnel_stage == "Awareness":

            monthly_table = monthly_summary[
                [
                    "Month",
                    "Spend",
                    "Impressions",
                    "CPM",
                    "Clicks",
                    "CTR",
                    "CPC",
                    "Completion_Rate"
                ]
            ].copy()

            monthly_table = monthly_table.rename(
                columns={
                    "Completion_Rate": "Completion Rate"
                }
            )


        elif funnel_stage == "Conversion":

            monthly_table = monthly_summary[
                [
                    "Month",
                    "Spend",
                    "Impressions",
                    "CPM",
                    "Clicks",
                    "CTR",
                    "CPC",
                    "Total Conversions",
                    "CPA",
                    "Conversion Rate",
                    "Revenue",
                    "ROAS"
                ]
            ].copy()


        else:

            monthly_table = monthly_summary[
                [
                    "Month",
                    "Spend"
                ]
            ].copy()


        numeric_columns_to_round = [
            "Spend",
            "CPM",
            "CTR",
            "CPC",
            "CPA",
            "Conversion Rate",
            "Revenue",
            "ROAS",
            "Completion Rate"
        ]


        for column in numeric_columns_to_round:

            if column in monthly_table.columns:

                monthly_table[column] = (
                    monthly_table[column]
                    .round(2)
                )


        st.dataframe(
            format_dataframe_for_display(monthly_table),
            use_container_width=True,
            hide_index=True
        )

# ---------------------------------------------------
# END SECTION 22
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 23: OPTIMIZATION ACTION CENTER
# ---------------------------------------------------
# TradeIQ turns analyzer output into a clutter-free decision workflow:
#
#   1. QUICK TRIAGE
#      A compact queue shows only the information needed to choose what to review.
#
#   2. DECISION BRIEF
#      Signal -> Root Cause -> Action -> Priority -> Risk
#
#   3. SUPPORTING EVIDENCE
#      Detailed metrics and guardrails stay behind tabs/expanders so the main
#      decision screen remains easy to scan.
#
#   4. TRADER DECISION
#      The trader can record Accept / Modify / Reject without leaving the page.
#
# The Action Center intentionally remains a decision-support system.
# It explains and documents the recommendation; it does not execute DSP changes.

elif page == "Optimization Action Center":

    import html as _html
    from pathlib import Path as _Path

    # ---------------------------------------------------
    # ACTION CENTER VISUAL SYSTEM
    # ---------------------------------------------------
    st.markdown(
        """
        <style>
        .tiq-action-header {
            margin-bottom: 0.25rem;
        }

        .tiq-action-subtitle {
            color: #9ca3af;
            margin-bottom: 1.0rem;
            line-height: 1.45;
        }

        .tiq-decision-hero {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
            padding: 1.05rem 1.15rem;
            background: rgba(255,255,255,0.025);
            margin: 0.35rem 0 0.9rem 0;
        }

        .tiq-decision-kicker {
            color: #9ca3af;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .tiq-decision-title {
            font-size: clamp(1.25rem, 1.7vw, 1.75rem);
            font-weight: 760;
            line-height: 1.15;
            margin-bottom: 0.35rem;
        }

        .tiq-decision-meta {
            color: #aeb6c2;
            font-size: 0.88rem;
            line-height: 1.4;
        }

        .tiq-brief-card {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 14px;
            padding: 0.95rem 1.05rem;
            background: rgba(255,255,255,0.018);
            margin-bottom: 0.7rem;
        }

        .tiq-brief-label {
            color: #9ca3af;
            font-size: 0.76rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.42rem;
        }

        .tiq-brief-text {
            font-size: 0.96rem;
            line-height: 1.55;
            margin: 0;
        }

        .tiq-action-step {
            margin-bottom: 0.45rem;
            line-height: 1.5;
        }

        .tiq-action-step:last-child {
            margin-bottom: 0;
        }

        .tiq-priority-high {
            color: #ff6b6b;
            font-weight: 750;
        }

        .tiq-priority-medium {
            color: #f0b95a;
            font-weight: 750;
        }

        .tiq-priority-low {
            color: #9ca3af;
            font-weight: 750;
        }

        .tiq-why-box {
            border-left: 4px solid rgba(255,255,255,0.35);
            padding: 0.8rem 1rem;
            background: rgba(255,255,255,0.025);
            border-radius: 0 10px 10px 0;
            margin: 0.85rem 0 0.35rem 0;
            line-height: 1.5;
        }

        .tiq-mini-note {
            color: #8f98a5;
            font-size: 0.80rem;
            line-height: 1.4;
        }

        /* Keep Action Center dataframes visually compact. */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-label tiq-action-header">Optimization Action Center</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div class="tiq-action-subtitle">
            Review the highest-impact decisions first. Open one recommendation to see the
            signal, evidence-based interpretation, exact action steps, urgency, and risk.
            Supporting metrics stay tucked away until you need them.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------
    def _finite_number(value, default=np.nan):
        try:
            value = float(value)
            return value if np.isfinite(value) else default
        except (TypeError, ValueError):
            return default


    def _safe_pct(value):
        value = _finite_number(value)
        return format_percent(value) if pd.notna(value) else "N/A"


    def _safe_money(value):
        value = _finite_number(value)
        return format_currency(value) if pd.notna(value) else "N/A"


    def _safe_multiplier(value):
        value = _finite_number(value)
        return format_multiplier(value) if pd.notna(value) else "N/A"


    def _html_text(value):
        return _html.escape(str(value if value is not None else "N/A"))


    def _priority_from_row(row):
        """
        Priority is intentionally row-aware rather than recommendation-only.

        High:
        - Strong evidence + meaningful spend exposure + a protective action
          (failed guardrail, negation/pause/avoid candidate).

        Medium:
        - Controlled scale/reduction/investigation with enough evidence to act.

        Low:
        - Weak evidence, maintain/watch, or gather-more-data situations.
        """
        recommendation = str(row.get("Recommendation", "")).upper().strip()
        evidence = str(row.get("Evidence Strength", "Weak")).title()
        spend_share = _finite_number(row.get("Spend Share", 0), 0)

        protective_actions = {
            "DO NOT SCALE - GUARDRAIL FAILED",
            "NEGATION CANDIDATE",
            "PAUSE CANDIDATE",
            "AVOID / REDUCE"
        }

        medium_actions = {
            "SCALE",
            "PRIORITIZE",
            "CONTROLLED TEST",
            "REDUCE",
            "REDUCE / INVESTIGATE",
            "REFRESH / REDUCE",
            "INVESTIGATE"
        }

        if (
            recommendation in protective_actions
            and evidence == "Strong"
            and spend_share >= 5
        ):
            return "P1 - Protect Performance"

        if recommendation in medium_actions and evidence in {"Strong", "Moderate"}:
            return "P2 - Optimize Soon"

        if (
            recommendation == "DO NOT SCALE - GUARDRAIL FAILED"
            and evidence in {"Strong", "Moderate"}
        ):
            return "P2 - Optimize Soon"

        return "P3 - Monitor / Gather Evidence"


    def _priority_guidance(priority):
        if priority == "P1 - Protect Performance":
            return (
                "High — review today",
                "tiq-priority-high"
            )
        if priority == "P2 - Optimize Soon":
            return (
                "Medium — act within 2–3 days",
                "tiq-priority-medium"
            )
        return (
            "Low — monitor or gather more evidence",
            "tiq-priority-low"
        )


    def _build_root_cause(row, analyzer_type):
        """
        Explain the observable relationship without overstating causality.
        We deliberately use 'indicates' / 'suggests' instead of claiming that
        the report proves a behavioral cause.
        """
        recommendation = str(row.get("Recommendation", "")).upper().strip()
        evidence = str(row.get("Evidence Strength", "Weak")).title()

        if funnel_stage == "Conversion":
            efficiency = _finite_number(row.get("Efficiency Index", np.nan))
            cpa_value = _finite_number(row.get("CPA", np.nan))
            roas_value = _finite_number(row.get("ROAS", np.nan))

            if pd.notna(efficiency):
                if efficiency >= 1.10:
                    relationship = (
                        f"Efficiency Index {_safe_multiplier(efficiency)} means this entity's "
                        f"conversion share is {efficiency:.2f}x its spend share. "
                        "The available evidence therefore indicates above-average conversion efficiency."
                    )
                elif efficiency <= 0.90:
                    relationship = (
                        f"Efficiency Index {_safe_multiplier(efficiency)} means conversion contribution "
                        "is not keeping pace with spend allocation. The available evidence indicates "
                        "below-average conversion efficiency."
                    )
                else:
                    relationship = (
                        f"Efficiency Index {_safe_multiplier(efficiency)} is close to the campaign "
                        "average of 1.00x, so the efficiency signal is not materially differentiated."
                    )
            else:
                relationship = (
                    "The report does not contain enough usable efficiency data to establish a "
                    "strong conversion-efficiency relationship."
                )

            kpi_context = []
            if pd.notna(cpa_value):
                kpi_context.append(
                    f"CPA is {_safe_money(cpa_value)} versus the "
                    f"{_safe_money(primary_kpi_goal) if primary_kpi == 'CPA' else str(primary_kpi) + ' goal'}"
                )
            if pd.notna(roas_value):
                kpi_context.append(
                    f"ROAS is {_safe_multiplier(roas_value)} versus the "
                    f"{_safe_multiplier(roas_goal)} goal"
                )

            return (
                relationship
                + (" " + "; ".join(kpi_context) + "." if kpi_context else "")
                + f" Evidence Strength is {evidence}."
            )

        completion_index = _finite_number(row.get("Completion Index", np.nan))
        viewability_index = _finite_number(row.get("Viewability Index", np.nan))
        cpm_efficiency = _finite_number(row.get("CPM Efficiency", np.nan))

        parts = []
        if pd.notna(completion_index):
            parts.append(
                f"Completion Index {_safe_multiplier(completion_index)} compares completion "
                "performance with the campaign average"
            )
        if analyzer_type in {"inventory", "domain"}:
            if pd.notna(viewability_index):
                parts.append(
                    f"Viewability Index {_safe_multiplier(viewability_index)} describes relative "
                    "supply quality"
                )
            if pd.notna(cpm_efficiency):
                parts.append(
                    f"CPM Efficiency {_safe_multiplier(cpm_efficiency)} describes relative supply cost"
                )

        if not parts:
            return (
                f"The available awareness data does not support a strong root-cause interpretation. "
                f"Evidence Strength is {evidence}."
            )

        return (
            ". ".join(parts)
            + f". These signals describe the observed delivery relationship; they do not prove "
              f"causality. Evidence Strength is {evidence}."
        )


    def _build_action_steps(row):
        """
        Create concrete but controlled execution guidance.

        Dollar ranges scale with the entity's existing spend so the recommendation
        remains useful for both small and large campaigns.
        """
        recommendation = str(row.get("Recommendation", "")).upper().strip()
        current_spend = max(_finite_number(row.get("Spend", 0), 0), 0)
        evidence = str(row.get("Evidence Strength", "Weak")).title()

        increase_low = current_spend * 0.05
        increase_high = current_spend * 0.10
        next_low = current_spend * 0.10
        next_high = current_spend * 0.20

        monitor_window = "3–5 days" if evidence == "Strong" else "5–7 days"

        primary_condition = ""
        if primary_kpi and primary_kpi_goal is not None:
            comparator = "<=" if primary_kpi in LOWER_IS_BETTER_KPIS else ">="
            primary_condition = (
                f"{primary_kpi} stays {comparator} "
                f"{format_metric_value(primary_kpi, primary_kpi_goal)}"
            )

        guardrail_conditions = []
        if primary_condition:
            guardrail_conditions.append(primary_condition)
        if roas_goal is not None:
            guardrail_conditions.append(
                f"ROAS stays >= {_safe_multiplier(roas_goal)}"
            )
        if secondary_kpi and secondary_kpi_goal is not None:
            comparator = "<=" if secondary_kpi in LOWER_IS_BETTER_KPIS else ">="
            guardrail_conditions.append(
                f"{secondary_kpi} stays {comparator} "
                f"{format_metric_value(secondary_kpi, secondary_kpi_goal)}"
            )

        condition_text = " and ".join(guardrail_conditions)

        positive_actions = {"SCALE", "PRIORITIZE", "CONTROLLED TEST"}
        negative_actions = {
            "NEGATION CANDIDATE", "PAUSE CANDIDATE", "AVOID / REDUCE",
            "REDUCE", "REDUCE / INVESTIGATE", "REFRESH / REDUCE"
        }

        if recommendation in positive_actions:
            return [
                (
                    f"Shift approximately {_safe_money(increase_low)}–{_safe_money(increase_high)} "
                    f"(5–10% of this entity's current spend) from lower-efficiency alternatives "
                    "where business and delivery constraints allow."
                ),
                (
                    f"Monitor the primary KPI, ROAS, secondary KPI, and conversion volume for "
                    f"{monitor_window}."
                ),
                (
                    f"If {condition_text}, consider another controlled increase of approximately "
                    f"{_safe_money(next_low)}–{_safe_money(next_high)} (10–20% of current spend)."
                    if condition_text
                    else
                    "If performance remains stable after the monitoring window, consider another "
                    "controlled increase rather than a large one-time reallocation."
                )
            ]

        if recommendation == "DO NOT SCALE - GUARDRAIL FAILED":
            return [
                "Hold additional budget on this entity; do not scale while a configured guardrail is failing.",
                "Use the analyzer diagnostics to identify which KPI is breaking and whether the issue is persistent or a short-term fluctuation.",
                (
                    f"Reconsider scale only after {condition_text} for a sustained observation window."
                    if condition_text
                    else
                    "Reconsider scale only after the failed guardrail has recovered and the signal remains supported."
                )
            ]

        if recommendation in negative_actions:
            reduction_low = current_spend * 0.15
            reduction_high = current_spend * 0.25
            return [
                "Validate that the signal is not caused by a reporting anomaly, short-lived delivery issue, or obvious interaction effect.",
                (
                    f"Start with a controlled reduction of approximately "
                    f"{_safe_money(reduction_low)}–{_safe_money(reduction_high)} "
                    f"(15–25% of this entity's current spend) rather than an immediate full stop."
                ),
                (
                    f"Monitor for {monitor_window}. If the campaign-level KPI improves while this "
                    "entity remains weak, consider a stronger reduction, pause, or negation."
                )
            ]

        if recommendation in {
            "GATHER MORE DATA", "INVESTIGATE - MORE DATA NEEDED", "INSUFFICIENT DATA"
        }:
            return [
                "Keep the current setup materially unchanged while more evidence accumulates.",
                "Review data quality and the relevant diagnostic metrics for obvious measurement or delivery issues.",
                "Re-evaluate once Evidence Strength improves or the KPI signal becomes materially stronger."
            ]

        if recommendation == "INVESTIGATE":
            return [
                "Open the relevant analyzer and identify which diagnostic metric is driving the weak signal.",
                "Check whether the issue is isolated to this entity or appears across related audience, creative, inventory, or domain dimensions.",
                "Make a controlled change only after the likely driver is identified."
            ]

        return [
            "Maintain the current setup.",
            "Continue monitoring the configured KPI guardrails.",
            "Revisit only if performance meaningfully changes or new evidence emerges."
        ]


    def _build_risk_text(row):
        recommendation = str(row.get("Recommendation", "")).upper().strip()
        evidence = str(row.get("Evidence Strength", "Weak")).title()
        efficiency = _finite_number(row.get("Efficiency Index", np.nan))
        warnings = int(_finite_number(row.get("Data_Quality_Warnings", 0), 0) or 0)

        positive_actions = {"SCALE", "PRIORITIZE", "CONTROLLED TEST"}

        if recommendation in positive_actions and pd.notna(efficiency):
            stressed_efficiency = efficiency * 0.85
            relative_to_average = (stressed_efficiency - 1.0) * 100

            if stressed_efficiency >= 1:
                comparison = (
                    f"Even then, the efficiency signal would remain approximately "
                    f"{relative_to_average:.0f}% above the 1.00x campaign average."
                )
            else:
                comparison = (
                    f"That would put the efficiency signal approximately "
                    f"{abs(relative_to_average):.0f}% below the 1.00x campaign average."
                )

            text = (
                f"If efficiency deteriorates by 15% after the allocation change, the Efficiency "
                f"Index would move from {_safe_multiplier(efficiency)} to "
                f"{_safe_multiplier(stressed_efficiency)}. {comparison} "
                "Scaling can change auction dynamics, available inventory, and marginal performance, "
                "so the current relationship should be revalidated after the change."
            )
        elif recommendation in {
            "NEGATION CANDIDATE", "PAUSE CANDIDATE", "AVOID / REDUCE",
            "REDUCE", "REDUCE / INVESTIGATE", "REFRESH / REDUCE"
        }:
            text = (
                "Reducing exposure too aggressively can remove incremental value if the observed "
                "underperformance is temporary, caused by another dimension, or affected by attribution "
                "noise. Use a controlled reduction and confirm campaign-level improvement before a hard stop."
            )
        elif evidence == "Weak":
            text = (
                "Evidence Strength is Weak. The observed result may be normal variance rather than a "
                "stable performance relationship, so a large optimization would be difficult to defend."
            )
        else:
            text = (
                "The current signal is not strong enough to justify a large change. Continue monitoring "
                "for a material shift in performance or guardrail status."
            )

        if warnings > 0:
            text += (
                f" There are also {warnings} data-quality warning(s) associated with this entity; "
                "review them before execution."
            )

        return text


    def _build_signal_text(row):
        if funnel_stage == "Conversion":
            conv_share = _finite_number(row.get("Conversion Share", np.nan))
            spend_share = _finite_number(row.get("Spend Share", np.nan))
            return (
                f"This {str(row.get('Analyzer', 'entity')).lower()} generates "
                f"{_safe_pct(conv_share)} of campaign conversions from "
                f"{_safe_pct(spend_share)} of campaign spend."
            )

        impression_share = _finite_number(row.get("Impression Share", np.nan))
        spend_share = _finite_number(row.get("Spend Share", np.nan))
        return (
            f"This {str(row.get('Analyzer', 'entity')).lower()} delivers "
            f"{_safe_pct(impression_share)} of campaign impressions from "
            f"{_safe_pct(spend_share)} of campaign spend."
        )


    def _build_why_it_matters(row):
        recommendation = str(row.get("Recommendation", "")).upper().strip()
        if recommendation in {"SCALE", "PRIORITIZE", "CONTROLLED TEST"}:
            return (
                "The trader can see the opportunity, the exact guardrails that must stay intact, "
                "and a controlled way to test additional allocation instead of making an all-or-nothing move."
            )
        if recommendation in {
            "DO NOT SCALE - GUARDRAIL FAILED",
            "NEGATION CANDIDATE", "PAUSE CANDIDATE", "AVOID / REDUCE",
            "REDUCE", "REDUCE / INVESTIGATE", "REFRESH / REDUCE"
        }:
            return (
                "The trader can explain why exposure should be protected or reduced, while showing "
                "that the decision was based on evidence rather than a single bad metric."
            )
        return (
            "The trader can document why no major action was taken yet and show that the decision "
            "was based on evidence strength and KPI guardrails."
        )


    def _build_action_evidence(row, analyzer_type):
        """Compact evidence string used only inside the queue."""
        evidence_parts = []

        if funnel_stage == "Conversion":
            evidence_parts.append(
                f"Eff {_safe_multiplier(row.get('Efficiency Index', np.nan))}"
            )
            evidence_parts.append(
                f"CPA {_safe_money(row.get('CPA', np.nan))}"
            )
            evidence_parts.append(
                f"ROAS {_safe_multiplier(row.get('ROAS', np.nan))}"
            )
        else:
            evidence_parts.append(
                f"Completion {_safe_multiplier(row.get('Completion Index', np.nan))}"
            )
            if analyzer_type in {"inventory", "domain"}:
                evidence_parts.append(
                    f"Viewability {_safe_multiplier(row.get('Viewability Index', np.nan))}"
                )
                evidence_parts.append(
                    f"CPM Eff {_safe_multiplier(row.get('CPM Efficiency', np.nan))}"
                )

        return " • ".join(evidence_parts)


    def append_actions(
        frames,
        result_df,
        analyzer_name,
        item_column,
        analyzer_type
    ):
        """Convert one analyzer result into one consistent decision table."""
        if result_df is None or result_df.empty:
            return

        required_columns = {item_column, "Recommendation"}
        if not required_columns.issubset(result_df.columns):
            return

        action_df = result_df.copy()
        action_df["Analyzer"] = analyzer_name
        action_df["Analyzer Type"] = analyzer_type
        action_df["Item"] = action_df[item_column].astype(str)

        # Build the Action Center's trader-facing narrative.
        action_df["Priority"] = action_df.apply(_priority_from_row, axis=1)
        action_df["Signal"] = action_df.apply(_build_signal_text, axis=1)
        action_df["Root Cause"] = action_df.apply(
            lambda row: _build_root_cause(row, analyzer_type),
            axis=1
        )
        action_df["Action Steps"] = action_df.apply(_build_action_steps, axis=1)
        action_df["Risk Scenario"] = action_df.apply(_build_risk_text, axis=1)
        action_df["Why It Matters"] = action_df.apply(_build_why_it_matters, axis=1)
        action_df["Evidence Summary"] = action_df.apply(
            lambda row: _build_action_evidence(row, analyzer_type),
            axis=1
        )

        action_df["_Spend"] = action_df.get(
            "Spend",
            pd.Series(0, index=action_df.index)
        )

        # Make every downstream column safe even when an analyzer does not use it.
        decision_columns = [
            "Priority", "Analyzer", "Analyzer Type", "Item", "Recommendation",
            "Evidence Strength", "Guardrail Status",
            "Primary Guardrail", "Secondary Guardrail", "ROAS Guardrail",
            "Signal", "Root Cause", "Action Steps", "Risk Scenario",
            "Why It Matters", "Evidence Summary", "_Spend",
            "Spend Share", "Conversion Share", "Impression Share",
            "Efficiency Index", "CPA", "ROAS", "Total Conversions",
            "Completion Rate", "Completion Index", "Viewability",
            "Viewability Index", "CPM", "CPM Efficiency",
            "Active_Days", "Data_Quality_Warnings"
        ]

        for column in decision_columns:
            if column not in action_df.columns:
                action_df[column] = np.nan if column not in {
                    "Priority", "Analyzer", "Analyzer Type", "Item",
                    "Recommendation", "Evidence Strength", "Guardrail Status",
                    "Primary Guardrail", "Secondary Guardrail", "ROAS Guardrail",
                    "Signal", "Root Cause", "Risk Scenario",
                    "Why It Matters", "Evidence Summary"
                } else ""

        frames.append(action_df[decision_columns])


    # ---------------------------------------------------
    # BUILD ONE DECISION QUEUE FROM ALL ANALYZERS
    # ---------------------------------------------------
    action_frames = []

    audience_actions = calculate_audience_recommendations(campaign_df)
    append_actions(
        action_frames,
        audience_actions,
        "Audience",
        "Audience_Segment",
        "audience"
    )

    if "Creative_Name" in campaign_df.columns:
        creative_actions = calculate_specialized_dimension_recommendations(
            campaign_df,
            "Creative_Name",
            "creative",
            metadata_columns=["Creative_Length_Sec"]
        )
        append_actions(
            action_frames,
            creative_actions,
            "Creative",
            "Creative_Name",
            "creative"
        )

    inventory_dimensions = {
        "Inventory - Channel": "Channel",
        "Inventory - Deal Type": "Deal_Type",
        "Inventory - Device Type": "Device_Type"
    }

    for analyzer_name, dimension_column in inventory_dimensions.items():
        if dimension_column not in campaign_df.columns:
            continue

        inventory_actions = calculate_specialized_dimension_recommendations(
            campaign_df,
            dimension_column,
            "inventory"
        )
        append_actions(
            action_frames,
            inventory_actions,
            analyzer_name,
            dimension_column,
            "inventory"
        )

    possible_action_domain_columns = [
        "Domain", "Site", "Website", "Domain_Name", "Site_Domain"
    ]
    action_domain_column = next(
        (
            column
            for column in possible_action_domain_columns
            if column in campaign_df.columns
        ),
        None
    )
    if action_domain_column is None and "Publisher" in campaign_df.columns:
        action_domain_column = "Publisher"

    if action_domain_column is not None:
        domain_actions = calculate_specialized_dimension_recommendations(
            campaign_df,
            action_domain_column,
            "domain"
        )
        append_actions(
            action_frames,
            domain_actions,
            "Domain / Website",
            action_domain_column,
            "domain"
        )

    if not action_frames:
        st.warning("No analyzer recommendations are available for this campaign.")

    else:
        action_center_df = pd.concat(action_frames, ignore_index=True)

        priority_order = {
            "P1 - Protect Performance": 1,
            "P2 - Optimize Soon": 2,
            "P3 - Monitor / Gather Evidence": 3
        }

        action_center_df["_Priority_Order"] = (
            action_center_df["Priority"]
            .map(priority_order)
            .fillna(4)
        )

        action_center_df = (
            action_center_df
            .sort_values(
                ["_Priority_Order", "_Spend"],
                ascending=[True, False]
            )
            .reset_index(drop=True)
        )

        # ---------------------------------------------------
        # QUICK TRIAGE SUMMARY
        # ---------------------------------------------------
        p1_count = int(
            (action_center_df["Priority"] == "P1 - Protect Performance").sum()
        )
        p2_count = int(
            (action_center_df["Priority"] == "P2 - Optimize Soon").sum()
        )
        p3_count = int(
            (action_center_df["Priority"] == "P3 - Monitor / Gather Evidence").sum()
        )

        render_tile_grid(
            [
                {
                    "label": "Protect Performance",
                    "value": f"{p1_count}",
                    "note": "Highest-risk items"
                },
                {
                    "label": "Optimize Soon",
                    "value": f"{p2_count}",
                    "note": "Controlled decisions"
                },
                {
                    "label": "Monitor",
                    "value": f"{p3_count}",
                    "note": "Weak / neutral signals"
                },
                {
                    "label": "Total Decisions",
                    "value": f"{len(action_center_df)}",
                    "note": "Across all analyzers"
                }
            ],
            compact=True
        )

        st.write("")

        # ---------------------------------------------------
        # CLUTTER-FREE QUEUE CONTROLS
        # ---------------------------------------------------
        control_col1, control_col2 = st.columns([1.15, 1], gap="medium")

        with control_col1:
            queue_view = st.selectbox(
                "Queue View",
                [
                    "Needs Action",
                    "All Decisions",
                    "Protect Performance",
                    "Optimize Soon",
                    "Monitor Only"
                ],
                key="action_center_queue_view",
                help="Needs Action hides low-priority monitor rows by default."
            )

        with control_col2:
            analyzer_options = ["All Areas"] + sorted(
                action_center_df["Analyzer"].dropna().astype(str).unique().tolist()
            )
            analyzer_filter = st.selectbox(
                "Area",
                analyzer_options,
                key="action_center_area_filter"
            )

        visible_actions = action_center_df.copy()

        if queue_view == "Needs Action":
            visible_actions = visible_actions[
                visible_actions["Priority"].isin(
                    ["P1 - Protect Performance", "P2 - Optimize Soon"]
                )
            ]
        elif queue_view == "Protect Performance":
            visible_actions = visible_actions[
                visible_actions["Priority"] == "P1 - Protect Performance"
            ]
        elif queue_view == "Optimize Soon":
            visible_actions = visible_actions[
                visible_actions["Priority"] == "P2 - Optimize Soon"
            ]
        elif queue_view == "Monitor Only":
            visible_actions = visible_actions[
                visible_actions["Priority"] == "P3 - Monitor / Gather Evidence"
            ]

        if analyzer_filter != "All Areas":
            visible_actions = visible_actions[
                visible_actions["Analyzer"] == analyzer_filter
            ]

        st.markdown("### Decision Queue")

        if visible_actions.empty:
            st.info("No decisions match the selected queue filters.")
        else:
            compact_queue = visible_actions[
                [
                    "Priority",
                    "Analyzer",
                    "Item",
                    "Recommendation",
                    "Evidence Strength",
                    "Guardrail Status"
                ]
            ].copy()

            compact_queue = compact_queue.rename(
                columns={
                    "Analyzer": "Area",
                    "Recommendation": "Decision",
                    "Evidence Strength": "Evidence",
                    "Guardrail Status": "Guardrails"
                }
            )

            st.dataframe(
                compact_queue,
                use_container_width=True,
                hide_index=True,
                height=min(420, 42 + len(compact_queue) * 35),
                column_config={
                    "Priority": st.column_config.TextColumn("Priority", width="medium"),
                    "Area": st.column_config.TextColumn("Area", width="medium"),
                    "Item": st.column_config.TextColumn("Item", width="large"),
                    "Decision": st.column_config.TextColumn("Decision", width="medium"),
                    "Evidence": st.column_config.TextColumn("Evidence", width="small"),
                    "Guardrails": st.column_config.TextColumn("Guardrails", width="small"),
                }
            )

        st.caption(
            "The queue is intentionally brief. Select a decision below for the full explanation."
        )

        # ---------------------------------------------------
        # SELECT ONE DECISION TO REVIEW
        # ---------------------------------------------------
        selection_source = (
            visible_actions
            if not visible_actions.empty
            else action_center_df
        )

        decision_labels = []
        decision_row_indices = []

        for idx, row in selection_source.iterrows():
            decision_labels.append(
                f"{row['Priority']}  |  {row['Analyzer']}  |  "
                f"{row['Item']}  |  {row['Recommendation']}"
            )
            decision_row_indices.append(idx)

        selected_label = st.selectbox(
            "Open Decision",
            decision_labels,
            key="action_center_open_decision"
        )

        selected_position = decision_labels.index(selected_label)
        selected_index = decision_row_indices[selected_position]
        selected_decision = action_center_df.loc[selected_index]

        priority_text, priority_css = _priority_guidance(
            selected_decision["Priority"]
        )

        st.markdown(
            f"""
            <div class="tiq-decision-hero">
                <div class="tiq-decision-kicker">
                    {_html_text(selected_decision['Analyzer'])} decision brief
                </div>
                <div class="tiq-decision-title">
                    {_html_text(selected_decision['Recommendation'])}
                    — {_html_text(selected_decision['Item'])}
                </div>
                <div class="tiq-decision-meta">
                    Evidence: <b>{_html_text(selected_decision['Evidence Strength'])}</b>
                    &nbsp;•&nbsp;
                    Guardrails: <b>{_html_text(selected_decision['Guardrail Status'])}</b>
                    &nbsp;•&nbsp;
                    Spend at stake: <b>{_html_text(_safe_money(selected_decision.get('_Spend', 0)))}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------------
        # MAIN DECISION BRIEF
        # ---------------------------------------------------
        st.markdown(
            f"""
            <div class="tiq-brief-card">
                <div class="tiq-brief-label">Signal</div>
                <p class="tiq-brief-text">
                    {_html_text(selected_decision.get('Signal', 'N/A'))}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="tiq-brief-card">
                <div class="tiq-brief-label">Root Cause / Interpretation</div>
                <p class="tiq-brief-text">
                    {_html_text(selected_decision.get('Root Cause', 'N/A'))}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        action_steps = selected_decision.get("Action Steps", [])
        if not isinstance(action_steps, list):
            action_steps = [str(action_steps)]

        action_html = "".join(
            f'<div class="tiq-action-step"><b>{step_number}.</b> '
            f'{_html_text(step)}</div>'
            for step_number, step in enumerate(action_steps, start=1)
        )

        st.markdown(
            f"""
            <div class="tiq-brief-card">
                <div class="tiq-brief-label">Action</div>
                {action_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        priority_col, risk_col = st.columns([0.85, 2.15], gap="medium")

        with priority_col:
            st.markdown(
                f"""
                <div class="tiq-brief-card">
                    <div class="tiq-brief-label">Priority</div>
                    <p class="tiq-brief-text {priority_css}">
                        {_html_text(priority_text)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with risk_col:
            st.markdown(
                f"""
                <div class="tiq-brief-card">
                    <div class="tiq-brief-label">Risk</div>
                    <p class="tiq-brief-text">
                        {_html_text(selected_decision.get('Risk Scenario', 'N/A'))}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"""
            <div class="tiq-why-box">
                <b>Why it matters:</b>
                {_html_text(selected_decision.get('Why It Matters', 'N/A'))}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------------
        # SUPPORTING DETAIL — HIDDEN UNTIL NEEDED
        # ---------------------------------------------------
        evidence_tab, guardrail_tab, record_tab = st.tabs(
            ["Decision Evidence", "Guardrails", "Record Decision"]
        )

        with evidence_tab:
            evidence_rows = []

            def add_evidence_row(metric, current, benchmark, interpretation):
                evidence_rows.append(
                    {
                        "Metric": metric,
                        "Current": current,
                        "Benchmark / Goal": benchmark,
                        "What it means": interpretation
                    }
                )

            if pd.notna(selected_decision.get("Spend Share", np.nan)):
                add_evidence_row(
                    "Spend Share",
                    _safe_pct(selected_decision.get("Spend Share")),
                    "Campaign allocation",
                    "Share of campaign spend assigned to this entity."
                )

            if funnel_stage == "Conversion":
                if pd.notna(selected_decision.get("Conversion Share", np.nan)):
                    add_evidence_row(
                        "Conversion Share",
                        _safe_pct(selected_decision.get("Conversion Share")),
                        "Campaign contribution",
                        "Share of campaign conversions generated by this entity."
                    )

                if pd.notna(selected_decision.get("Efficiency Index", np.nan)):
                    add_evidence_row(
                        "Efficiency Index",
                        _safe_multiplier(selected_decision.get("Efficiency Index")),
                        "1.00x campaign average",
                        "Conversion Share divided by Spend Share."
                    )

                if pd.notna(selected_decision.get("CPA", np.nan)):
                    add_evidence_row(
                        "CPA",
                        _safe_money(selected_decision.get("CPA")),
                        (
                            format_metric_value(primary_kpi, primary_kpi_goal)
                            if primary_kpi == "CPA"
                            else "Diagnostic"
                        ),
                        "Cost per conversion for this entity."
                    )

                if pd.notna(selected_decision.get("ROAS", np.nan)):
                    add_evidence_row(
                        "ROAS",
                        _safe_multiplier(selected_decision.get("ROAS")),
                        _safe_multiplier(roas_goal),
                        "Attributed revenue returned per $1 of spend."
                    )

                if pd.notna(selected_decision.get("Total Conversions", np.nan)):
                    add_evidence_row(
                        "Conversions",
                        format_compact_number(
                            selected_decision.get("Total Conversions")
                        ),
                        "Evidence volume",
                        "Observed conversion volume used in Evidence Strength."
                    )

            else:
                if pd.notna(selected_decision.get("Impression Share", np.nan)):
                    add_evidence_row(
                        "Impression Share",
                        _safe_pct(selected_decision.get("Impression Share")),
                        "Campaign contribution",
                        "Share of campaign impressions delivered by this entity."
                    )

                if pd.notna(selected_decision.get("Completion Index", np.nan)):
                    add_evidence_row(
                        "Completion Index",
                        _safe_multiplier(selected_decision.get("Completion Index")),
                        "1.00x campaign average",
                        "Relative video completion performance."
                    )

                if pd.notna(selected_decision.get("Viewability", np.nan)):
                    add_evidence_row(
                        "Viewability",
                        _safe_pct(selected_decision.get("Viewability")),
                        (
                            format_metric_value(secondary_kpi, secondary_kpi_goal)
                            if secondary_kpi == "Viewability"
                            else "Diagnostic"
                        ),
                        "Observed viewability for the entity."
                    )

                if pd.notna(selected_decision.get("CPM", np.nan)):
                    add_evidence_row(
                        "CPM",
                        _safe_money(selected_decision.get("CPM")),
                        "Campaign context",
                        "Cost per thousand impressions."
                    )

            add_evidence_row(
                "Evidence Strength",
                str(selected_decision.get("Evidence Strength", "N/A")),
                "Strong / Moderate / Weak",
                "Volume, spend share, and active days supporting the decision."
            )

            evidence_df = pd.DataFrame(evidence_rows)
            st.dataframe(
                evidence_df,
                use_container_width=True,
                hide_index=True
            )

            with st.expander("Methodology", expanded=False):
                if funnel_stage == "Conversion":
                    st.markdown(
                        """
                        **Evidence Strength**
                        - Strong: Spend Share ≥ 5%, 50+ conversions, 7+ active days
                        - Moderate: Spend Share ≥ 2%, 20+ conversions, 3+ active days
                        - Weak: Below those floors

                        **Efficiency Index**
                        - 1.00x = conversion contribution matches spend allocation
                        - >1.00x = conversion contribution exceeds spend allocation
                        - <1.00x = conversion contribution trails spend allocation
                        """
                    )
                else:
                    st.markdown(
                        """
                        **Evidence Strength**
                        - Strong: Spend Share ≥ 5%, 2M+ impressions, 7+ active days
                        - Moderate: Spend Share ≥ 2%, 500K+ impressions, 3+ active days
                        - Weak: Below those floors
                        """
                    )

        with guardrail_tab:
            guardrail_rows = []

            primary_actual = selected_decision.get(primary_kpi, np.nan)
            guardrail_rows.append(
                {
                    "Guardrail": f"Primary KPI — {primary_kpi}",
                    "Current": (
                        format_metric_value(primary_kpi, primary_actual)
                        if pd.notna(primary_actual) else "N/A"
                    ),
                    "Goal": format_metric_value(primary_kpi, primary_kpi_goal),
                    "Status": selected_decision.get("Primary Guardrail", "N/A")
                }
            )

            if secondary_kpi:
                secondary_actual = selected_decision.get(secondary_kpi, np.nan)
                guardrail_rows.append(
                    {
                        "Guardrail": f"Secondary KPI — {secondary_kpi}",
                        "Current": (
                            format_metric_value(secondary_kpi, secondary_actual)
                            if pd.notna(secondary_actual) else "N/A"
                        ),
                        "Goal": format_metric_value(
                            secondary_kpi, secondary_kpi_goal
                        ),
                        "Status": selected_decision.get(
                            "Secondary Guardrail", "N/A"
                        )
                    }
                )

            roas_actual = selected_decision.get("ROAS", np.nan)
            guardrail_rows.append(
                {
                    "Guardrail": "ROAS",
                    "Current": (
                        _safe_multiplier(roas_actual)
                        if pd.notna(roas_actual) else "N/A"
                    ),
                    "Goal": _safe_multiplier(roas_goal),
                    "Status": selected_decision.get("ROAS Guardrail", "N/A")
                }
            )

            st.dataframe(
                pd.DataFrame(guardrail_rows),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "PASS = goal met • CONDITIONAL = within the tolerance band • "
                "FAIL = materially outside goal • NOT AVAILABLE = report cannot validate it."
            )

        with record_tab:
            st.caption(
                "Document the trader's final decision without leaving the Action Center."
            )

            trader_decision = st.selectbox(
                "Trader Decision",
                ["Accept", "Modify", "Reject"],
                key="action_center_trader_decision"
            )

            action_taken = st.text_area(
                "Action Taken / Planned",
                value=(
                    action_steps[0]
                    if action_steps
                    else ""
                ),
                height=90,
                key="action_center_action_taken"
            )

            expected_outcome = st.text_input(
                "Expected Outcome",
                value=(
                    f"Protect {primary_kpi} and ROAS while validating the recommendation."
                ),
                key="action_center_expected_outcome"
            )

            decision_note = st.text_area(
                "Trader Note (optional)",
                placeholder="Add business context, client constraints, or why you modified/rejected the recommendation.",
                height=80,
                key="action_center_trader_note"
            )

            save_decision = st.button(
                "Save to Optimization Tracker",
                type="primary",
                use_container_width=True,
                key="action_center_save_decision"
            )

            if save_decision:
                optimization_log_path = "data/optimization_log.csv"
                optimization_log_columns = [
                    "Date", "Campaign", "Area", "Entity", "TradeIQ Recommendation",
                    "Evidence Strength", "Guardrail Status", "Trader Decision",
                    "Action Taken", "Decision Evidence", "Risk", "Reason",
                    "Expected Outcome"
                ]

                try:
                    existing_log = pd.read_csv(optimization_log_path)
                    for column in optimization_log_columns:
                        if column not in existing_log.columns:
                            existing_log[column] = ""
                    existing_log = existing_log[optimization_log_columns]
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    existing_log = pd.DataFrame(
                        columns=optimization_log_columns
                    )

                decision_evidence_text = (
                    f"{selected_decision.get('Evidence Summary', '')} | "
                    f"Signal: {selected_decision.get('Signal', '')}"
                )

                reason_text = (
                    f"Root Cause: {selected_decision.get('Root Cause', '')}"
                )
                if decision_note.strip():
                    reason_text += f" | Trader Note: {decision_note.strip()}"

                new_log_row = pd.DataFrame(
                    [
                        {
                            "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                            "Campaign": selected_campaign,
                            "Area": selected_decision["Analyzer"],
                            "Entity": selected_decision["Item"],
                            "TradeIQ Recommendation": selected_decision["Recommendation"],
                            "Evidence Strength": selected_decision["Evidence Strength"],
                            "Guardrail Status": selected_decision["Guardrail Status"],
                            "Trader Decision": trader_decision,
                            "Action Taken": action_taken.strip(),
                            "Decision Evidence": decision_evidence_text,
                            "Risk": selected_decision.get("Risk Scenario", ""),
                            "Reason": reason_text,
                            "Expected Outcome": expected_outcome.strip()
                        }
                    ]
                )

                updated_log = pd.concat(
                    [existing_log, new_log_row],
                    ignore_index=True
                )

                _Path(optimization_log_path).parent.mkdir(
                    parents=True,
                    exist_ok=True
                )
                updated_log.to_csv(
                    optimization_log_path,
                    index=False
                )

                st.success(
                    "Decision saved to the Optimization Tracker with the evidence "
                    "available at decision time."
                )

        # ---------------------------------------------------
        # OPTIONAL EXPORT — KEPT OUT OF THE MAIN DECISION FLOW
        # ---------------------------------------------------
        with st.expander("Export Decision Brief", expanded=False):
            export_row = {
                "Campaign": selected_campaign,
                "Area": selected_decision["Analyzer"],
                "Entity": selected_decision["Item"],
                "Recommendation": selected_decision["Recommendation"],
                "Priority": selected_decision["Priority"],
                "Evidence Strength": selected_decision["Evidence Strength"],
                "Guardrail Status": selected_decision["Guardrail Status"],
                "Signal": selected_decision["Signal"],
                "Root Cause / Interpretation": selected_decision["Root Cause"],
                "Action": " | ".join(action_steps),
                "Risk": selected_decision["Risk Scenario"],
                "Why It Matters": selected_decision["Why It Matters"]
            }

            st.download_button(
                "Download Decision Brief (CSV)",
                data=pd.DataFrame([export_row]).to_csv(index=False).encode("utf-8"),
                file_name="tradeiq_decision_brief.csv",
                mime="text/csv",
                use_container_width=True
            )

# ---------------------------------------------------
# END SECTION 23
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 24: CHANGE LOG / OPTIMIZATION TRACKER
# ---------------------------------------------------
# Logs trading optimizations by campaign and keeps a
# simple local history in data/optimization_log.csv.
# This first version focuses on recording the decision,
# rationale, and expected outcome. Before/after impact
# measurement can be layered on later.

elif page == "Optimization Tracker":
    st.markdown(
        '<div class="section-label">Decision Log / Optimization Tracker</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Preserve what TradeIQ knew at decision time, what the trader chose to do, "
        "and why. The purpose is to make each optimization auditable and defensible later."
    )

    optimization_log_path = "data/optimization_log.csv"
    optimization_log_columns = [
        "Date", "Campaign", "Area", "Entity", "TradeIQ Recommendation",
        "Evidence Strength", "Guardrail Status", "Trader Decision",
        "Action Taken", "Decision Evidence", "Risk", "Reason", "Expected Outcome"
    ]

    def load_optimization_log():
        try:
            log_df = pd.read_csv(optimization_log_path)
            for column in optimization_log_columns:
                if column not in log_df.columns:
                    log_df[column] = ""
            return log_df[optimization_log_columns]
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=optimization_log_columns)

    def save_optimization_log(log_df):
        from pathlib import Path
        Path(optimization_log_path).parent.mkdir(parents=True, exist_ok=True)
        log_df.to_csv(optimization_log_path, index=False)

    optimization_log_df = load_optimization_log()
    campaign_history = optimization_log_df[
        optimization_log_df["Campaign"].astype(str) == str(selected_campaign)
    ].copy()

    total_changes = len(campaign_history)
    latest_change = "—"
    accepted_decisions = 0
    if not campaign_history.empty:
        parsed_dates = pd.to_datetime(campaign_history["Date"], errors="coerce")
        if parsed_dates.notna().any():
            latest_change = parsed_dates.max().strftime("%b %d, %Y")
        accepted_decisions = int(
            campaign_history["Trader Decision"].astype(str).str.startswith("Accept").sum()
        )

    render_tile_grid(
        [
            {"label": "Logged Decisions", "value": format_compact_number(total_changes), "note": "Selected campaign"},
            {"label": "Accepted / Modified", "value": format_compact_number(accepted_decisions), "note": "Trader-owned decisions"},
            {"label": "Latest Decision", "value": latest_change, "note": "Most recent audit record"}
        ],
        compact=True
    )

    st.markdown("### Record a Decision")
    st.caption(
        "Copy the evidence/guardrail details from the Action Center scorecard. "
        "The trader remains the final decision maker: accept, modify, reject, or defer."
    )

    available_areas = [
        "Audience", "Creative", "Inventory - Channel", "Inventory - Deal Type",
        "Inventory - Device Type", "Domain / Website", "Budget / Pacing",
        "Bid / Base Bid", "Frequency", "Other"
    ]
    trader_decisions = [
        "Accept Recommendation", "Accept with Modification",
        "Reject Recommendation", "Defer / Gather More Data"
    ]
    action_options = [
        "No Change Yet", "Increased Allocation", "Reduced Allocation",
        "Increased Bid", "Reduced Bid", "Paused", "Activated",
        "Excluded / Negated", "Added / Included", "Refreshed Creative",
        "Adjusted Frequency", "Other"
    ]
    recommendation_options = [
        "SCALE", "PRIORITIZE", "CONTROLLED TEST",
        "DO NOT SCALE - GUARDRAIL FAILED", "GATHER MORE DATA",
        "NEGATION CANDIDATE", "PAUSE CANDIDATE", "AVOID / REDUCE",
        "REDUCE", "REDUCE / INVESTIGATE", "REFRESH / REDUCE",
        "INVESTIGATE", "INVESTIGATE - MORE DATA NEEDED", "MAINTAIN", "WATCH", "Other"
    ]

    with st.form("optimization_tracker_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            optimization_date = st.date_input("Decision Date", value=pd.Timestamp.today().date())
            optimization_area = st.selectbox("Analyzer / Area", available_areas)
            optimization_entity = st.text_input("Entity", placeholder="e.g., Auto Intenders")
            tradeiq_recommendation = st.selectbox("TradeIQ Recommendation", recommendation_options)
            evidence_strength = st.selectbox("Evidence Strength", ["Strong", "Moderate", "Weak"])
            guardrail_status = st.selectbox("Guardrail Status", ["Passed", "Conditional", "Failed", "Incomplete"])

        with col2:
            trader_decision = st.selectbox("Trader Decision", trader_decisions)
            optimization_action = st.selectbox("Action Taken", action_options)
            decision_evidence = st.text_area(
                "Decision Evidence",
                placeholder="Paste the scorecard signal + KPI/guardrail evidence used at decision time.",
                height=95
            )
            optimization_risk = st.text_area(
                "Risk / What could make this wrong",
                placeholder="e.g., evidence is moderate; CPA may deteriorate if spend expands.",
                height=80
            )
            optimization_reason = st.text_area(
                "Trader Rationale",
                placeholder="Why did you accept, modify, reject, or defer the recommendation?",
                height=80
            )
            optimization_outcome = st.text_area(
                "Expected Outcome",
                placeholder="e.g., Improve CPA while maintaining ROAS and viewability guardrails.",
                height=80
            )

        submitted_optimization = st.form_submit_button("Save Decision Record", use_container_width=True)

    if submitted_optimization:
        missing_fields = []
        for label, value in [
            ("Entity", optimization_entity),
            ("Decision Evidence", decision_evidence),
            ("Trader Rationale", optimization_reason),
            ("Expected Outcome", optimization_outcome)
        ]:
            if not str(value).strip():
                missing_fields.append(label)

        if missing_fields:
            st.error("Please complete: " + ", ".join(missing_fields) + ".")
        else:
            new_record = pd.DataFrame([{
                "Date": optimization_date.strftime("%Y-%m-%d"),
                "Campaign": selected_campaign,
                "Area": optimization_area,
                "Entity": optimization_entity.strip(),
                "TradeIQ Recommendation": tradeiq_recommendation,
                "Evidence Strength": evidence_strength,
                "Guardrail Status": guardrail_status,
                "Trader Decision": trader_decision,
                "Action Taken": optimization_action,
                "Decision Evidence": decision_evidence.strip(),
                "Risk": optimization_risk.strip(),
                "Reason": optimization_reason.strip(),
                "Expected Outcome": optimization_outcome.strip()
            }])
            optimization_log_df = pd.concat([optimization_log_df, new_record], ignore_index=True)
            try:
                save_optimization_log(optimization_log_df)
                st.success("Decision record saved to the audit log.")
                st.rerun()
            except Exception as error:
                st.error(f"Unable to save the decision log: {error}")

    st.markdown("### Decision History")
    optimization_log_df = load_optimization_log()
    campaign_history = optimization_log_df[
        optimization_log_df["Campaign"].astype(str) == str(selected_campaign)
    ].copy()

    if campaign_history.empty:
        st.info("No decision records have been logged for this campaign yet.")
    else:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            area_filter_options = ["All Areas"] + sorted(
                campaign_history["Area"].dropna().astype(str).unique().tolist()
            )
            history_area_filter = st.selectbox("Area Filter", area_filter_options, key="optimization_history_area_filter")
        with filter_col2:
            history_search = st.text_input(
                "Search History",
                placeholder="Search entity, recommendation, evidence, rationale, or outcome",
                key="optimization_history_search"
            )

        visible_history = campaign_history.copy()
        if history_area_filter != "All Areas":
            visible_history = visible_history[visible_history["Area"] == history_area_filter]
        if history_search.strip():
            search_text = history_search.strip().lower()
            searchable_columns = [
                "Entity", "TradeIQ Recommendation", "Trader Decision", "Action Taken",
                "Decision Evidence", "Risk", "Reason", "Expected Outcome"
            ]
            search_mask = pd.Series(False, index=visible_history.index)
            for column in searchable_columns:
                search_mask = search_mask | (
                    visible_history[column].fillna("").astype(str).str.lower().str.contains(search_text, regex=False)
                )
            visible_history = visible_history[search_mask]

        visible_history["_Date_Sort"] = pd.to_datetime(visible_history["Date"], errors="coerce")
        visible_history = visible_history.sort_values("_Date_Sort", ascending=False)
        history_display = visible_history[
            [
                "Date", "Area", "Entity", "TradeIQ Recommendation", "Evidence Strength",
                "Guardrail Status", "Trader Decision", "Action Taken", "Decision Evidence",
                "Risk", "Reason", "Expected Outcome"
            ]
        ].copy()

        st.dataframe(history_display, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Decision History",
            data=history_display.to_csv(index=False).encode("utf-8"),
            file_name=str(selected_campaign).replace(" ", "_").replace("/", "-") + "_decision_history.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(
            "The audit log stores the evidence and trader rationale that existed when the decision was made. "
            "This makes later review possible even if campaign performance changes afterward."
        )

# ---------------------------------------------------
# END SECTION 24
# ---------------------------------------------------


# ---------------------------------------------------
# SECTION 25: AUDIENCE ANALYZER PAGE
# ---------------------------------------------------

elif page == "Audience Analyzer":
    render_clean_analyzer("Audience", "Audience_Segment", "audience")

elif page == "Creative Analyzer":
    render_clean_analyzer("Creative", "Creative_Name", "creative")

elif page == "Inventory Analyzer":
    render_clean_analyzer("Inventory", "Deal_Type", "inventory")

elif page == "Domain / Website Analyzer":
    render_clean_analyzer("Domain / Website", "Site_Domain", "domain")


elif page == "Pacing & Delivery Analyzer":
    render_pacing_delivery_analyzer()
