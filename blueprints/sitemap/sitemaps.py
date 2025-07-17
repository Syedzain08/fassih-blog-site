from flask import Blueprint, Response
from urllib.parse import quote

from db_models import Articles, Products


sitemap_bp = Blueprint("sitemap", __name__)


@sitemap_bp.route("/sitemap.xml", methods=["GET"])
def sitemap():
    domain = "https://vet-insights.com"

    static_urls = [
        {"loc": f"{domain}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{domain}/articles/", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{domain}/store/", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{domain}/search", "priority": "0.5", "changefreq": "weekly"},
    ]

    articles = Articles.query.filter_by(status="public").all()
    article_urls = [
        {
            "loc": f"{domain}/articles/{quote(a.slug)}",
            "lastmod": a.created_at.date().isoformat(),
            "priority": "0.7",
            "changefreq": "weekly",
        }
        for a in articles
    ]

    products = Products.query.filter_by(in_stock=True).all()
    product_urls = [
        {
            "loc": f"{domain}/store/view/product/{quote(p.slug)}",
            "lastmod": p.created_at.date().isoformat(),
            "priority": "0.7",
            "changefreq": "weekly",
        }
        for p in products
    ]

    urls = static_urls + article_urls + product_urls

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        xml.append("  <url>")
        xml.append(f'    <loc>{url["loc"]}</loc>')
        if "lastmod" in url:
            xml.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
        xml.append(f'    <changefreq>{url["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{url["priority"]}</priority>')
        xml.append("  </url>")

    xml.append("</urlset>")

    return Response("\n".join(xml), mimetype="application/xml")
