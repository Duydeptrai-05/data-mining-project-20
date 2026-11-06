"""C7: sinh file export Superset (chart 1-3) từ view mart của B. Import: Dashboards > Import (dashboard_C.zip).
Chỉ đọc schema mart (role superset_ro). Tiêu đề chart là kết luận kèm n, lấy từ outputs/results.json."""
import uuid, zipfile, yaml, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "dashboard_C.zip"
DB_UUID = "294f3b72-ba42-4805-b3d2-ad83b0388ac7"  # cùng database PostgreSQL với export của D
NS = uuid.UUID("6f0c7c00-0000-4000-8000-0000000000c7")
U = lambda name: str(uuid.uuid5(NS, name))

def col(name, typ, dttm=False):
    return dict(column_name=name, verbose_name=None, is_dttm=dttm, is_active=True, type=typ, advanced_data_type=None,
                groupby=True, filterable=True, expression=None, description=None, python_date_format=None,
                datetime_format=None, extra=None)

def dataset(view, cols):
    return dict(table_name=view, main_dttm_col=None, description=None, default_endpoint=None, offset=0, cache_timeout=None,
                catalog="dm_course", schema="mart", sql=None, params=None, template_params=None, filter_select_enabled=True,
                fetch_values_predicate=None, extra=None, normalize_columns=False, always_filter_main_dttm=False, folders=None,
                uuid=U("ds_" + view),
                metrics=[dict(metric_name="count", verbose_name="COUNT(*)", metric_type="count", expression="COUNT(*)",
                              description=None, d3format=None, currency=None, extra=None, warning_text=None)],
                columns=[col(n, t) for n, t in cols], version="1.0.0", database_uuid=DB_UUID)

DS = {
 "v_lowrated_by_category": [("category","TEXT"),("n_apps","BIGINT"),("n_low","BIGINT"),("low_rate","NUMERIC"),("ci_low","NUMERIC"),("ci_high","NUMERIC"),("n_enough","BOOLEAN")],
 "v_rating_by_price": [("price_type","TEXT"),("price_band","TEXT"),("band_order","INTEGER"),("n_apps","BIGINT"),("median_rating","NUMERIC"),("avg_rating","NUMERIC"),("n_enough","BOOLEAN")],
 "v_lowrated_by_age_install": [("dimension","TEXT"),("band","TEXT"),("band_order","INTEGER"),("n_apps","BIGINT"),("n_low","BIGINT"),("low_rate","NUMERIC"),("ci_low","NUMERIC"),("ci_high","NUMERIC"),("n_enough","BOOLEAN")],
}

def metric(colname, agg="MAX"):
    return dict(expressionType="SIMPLE", column=dict(column_name=colname), aggregate=agg, label=f"{agg}({colname})", hasCustomLabel=False)

def flt(subject, op, val, i):
    return dict(clause="WHERE", comparator=val, expressionType="SIMPLE", operator=op, subject=subject, filterOptionName=f"f{i}")

def bar(title, view, x, y_col, horizontal, filters, sort_desc, extra_cols=(), y_title="", xaxis_sort=None):
    p = dict(viz_type="echarts_timeseries_bar", datasource="__table", x_axis=x, metrics=[metric(y_col)], groupby=list(extra_cols),
             adhoc_filters=[flt(*f, i) for i, f in enumerate(filters)], orientation="horizontal" if horizontal else "vertical",
             row_limit=100, order_desc=sort_desc, show_legend=bool(extra_cols), show_value=True, y_axis_format=".1%" if "rate" in y_col else ",.2f",
             x_axis_title=x, y_axis_title=y_title, rich_tooltip=True, color_scheme="supersetColors", truncateYAxis=False, y_axis_bounds=[0, None],
             sort_series_type="sum", x_axis_sort=xaxis_sort or y_col, x_axis_sort_asc=not sort_desc)
    return dict(slice_name=title, description=None, certified_by=None, certification_details=None, viz_type="echarts_timeseries_bar",
                params=p, query_context=None, cache_timeout=None, uuid=U("ch_" + title[:30]), version="1.0.0", dataset_uuid=U("ds_" + view))

R = json.load(open(ROOT / "outputs" / "results.json"))["parts"]
f = R["nb03_funnel"]; perm = R["nb05_permutation"]
cat = sorted([r for r in R["nb03_low_rate_by_category"] if r["enough_n"]], key=lambda r: -r["rate"])[0]
age = {r["age_band"]: r for r in R["nb03_low_rate_by_age_band"]}
ins = {r["install_band"]: r for r in R["nb03_low_rate_by_install_band"]}
pct = lambda x: f"{x*100:.1f}".replace(".", ",") + "%"
nn = lambda x: f"{x:,}".replace(",", " ")

charts = [
 bar(f"{cat['category']} có tỉ lệ app điểm thấp cao nhất ({pct(cat['rate'])}, n = {cat['n']}), nhưng chênh lệch giữa danh mục chưa vượt nhiễu (hoán vị p ≈ {perm['p_value_exploratory']:.2f}; n = {nn(f['n_analysis'])} app)".replace("0.12","0,12"),
     "v_lowrated_by_category", "category", "low_rate", True, [("n_enough","==",True)], True, y_title="Tỉ lệ app Rating ≤ 3,0"),
 bar(f"App trả phí và miễn phí không khác nhau ổn định: dấu chênh lệch đổi giữa các cấu hình kiểm chứng (n = {nn(f['n_analysis'])} app; ô n < 30 ẩn)",
     "v_rating_by_price", "price_band", "median_rating", False, [("n_enough","==",True)], False, y_title="Điểm trung vị", xaxis_sort="band_order"),
 bar(f"Tỉ lệ điểm thấp cao nhất ở nhóm cập nhật 1–2 năm trước ({pct(age['1-2y']['rate'])}, n = {age['1-2y']['n']}), thấp nhất ở nhóm ≤ 3 tháng ({pct(age['<=3m']['rate'])}, n = {nn(age['<=3m']['n'])}); không đơn điệu",
     "v_lowrated_by_age_install", "band", "low_rate", False, [("dimension","==","age"),("n_enough","==",True)], False, y_title="Tỉ lệ app Rating ≤ 3,0", xaxis_sort="band_order"),
 bar(f"Tỉ lệ điểm thấp giảm khi lượt cài tăng: {pct(ins['10K-100K']['rate'])} ở 10K–100K (n = {nn(ins['10K-100K']['n'])}) xuống {pct(ins['10M+']['rate'])} ở 10M+ (n = {nn(ins['10M+']['n'])}); đi cùng, không phải nguyên nhân",
     "v_lowrated_by_age_install", "band", "low_rate", False, [("dimension","==","install"),("n_enough","==",True)], False, y_title="Tỉ lệ app Rating ≤ 3,0", xaxis_sort="band_order"),
]
for c in charts: c["uuid"] = U("ch_" + c["slice_name"][:40] + c["params"]["adhoc_filters"][0]["comparator"].__str__())

# Dashboard
rows, children = {}, {}
pos = {"DASHBOARD_VERSION_KEY": "v2", "ROOT_ID": dict(children=["GRID_ID"], id="ROOT_ID", type="ROOT"),
       "GRID_ID": dict(children=[], id="GRID_ID", parents=["ROOT_ID"], type="GRID"),
       "HEADER_ID": dict(id="HEADER_ID", meta=dict(text="C7 – Chart 1–3: danh mục, giá, độ cũ và lượt cài"), type="HEADER")}
pos["MARKDOWN-C7"] = dict(children=[], id="MARKDOWN-C7", meta=dict(width=12, height=20, code="**Lưu ý khi đọc:** cấp phân tích là APP, chỉ app có điểm và store_reviews ≥ 50; \"đi cùng\" không phải \"gây ra\"; ô n < 30 không diễn giải; dữ liệu đến 2018-08."), parents=["ROOT_ID","GRID_ID","ROW-C7-0"], type="MARKDOWN")
pos["ROW-C7-0"] = dict(children=["MARKDOWN-C7"], id="ROW-C7-0", meta=dict(background="BACKGROUND_TRANSPARENT"), parents=["ROOT_ID","GRID_ID"], type="ROW")
pos["GRID_ID"]["children"].append("ROW-C7-0")
for i, c in enumerate(charts):
    rid, cid = f"ROW-C7-{i+1}", f"CHART-C7-{i+1}"
    pos[cid] = dict(children=[], id=cid, meta=dict(chartId=i+1, height=60, sliceName=c["slice_name"], uuid=c["uuid"], width=12), parents=["ROOT_ID","GRID_ID",rid], type="CHART")
    pos[rid] = dict(children=[cid], id=rid, meta=dict(background="BACKGROUND_TRANSPARENT"), parents=["ROOT_ID","GRID_ID"], type="ROW")
    pos["GRID_ID"]["children"].append(rid)
dash = dict(dashboard_title="C7 – Chart 1–3 (danh mục, giá, độ cũ, lượt cài)", description=None, css="", slug=None, certified_by="", certification_details="",
            published=True, uuid=U("dash"), position=pos, metadata=dict(native_filter_configuration=[], chart_configuration={}, color_scheme="", refresh_frequency=0,
            cross_filters_enabled=False, default_filters="{}"), theme_uuid=None, version="1.0.0")

root = "dashboard_export_C7"
dump = lambda o: yaml.safe_dump(o, allow_unicode=True, sort_keys=False)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(f"{root}/metadata.yaml", dump(dict(version="1.0.0", type="Dashboard", timestamp="2026-11-06T00:00:00+00:00")))
    z.writestr(f"{root}/databases/PostgreSQL.yaml", dump(dict(database_name="PostgreSQL", sqlalchemy_uri="postgresql+psycopg2://superset_ro:XXXXXXXXXX@host.docker.internal:5432/dm_course",
        cache_timeout=None, expose_in_sqllab=True, allow_run_async=False, allow_ctas=False, allow_cvas=False, allow_dml=False, allow_file_upload=False,
        extra=dict(metadata_params={}, engine_params={}, metadata_cache_timeout={}, schemas_allowed_for_file_upload=[]), impersonate_user=False,
        configuration_method="sqlalchemy_form", uuid=DB_UUID, version="1.0.0")))
    for v, cols in DS.items():
        z.writestr(f"{root}/datasets/PostgreSQL/{v}.yaml", dump(dataset(v, cols)))
    for i, c in enumerate(charts):
        z.writestr(f"{root}/charts/chart_C7_{i+1}.yaml", dump(c))
    z.writestr(f"{root}/dashboards/C7_chart_1_3.yaml", dump(dash))
print("wrote", OUT, len(charts), "charts")
