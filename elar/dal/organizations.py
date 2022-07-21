from elar import db
from flask import request, url_for
from elar.models import Organization
from sqlalchemy import or_
import re


def query_organizations(per_page=25):
    description = request.args.get('description', None)
    query = Organization.query
    query = db.session.query(
        Organization.id,
        Organization.name,
        Organization.phone,
        Organization.address,
        Organization.organization_number,
        Organization.address2,
        Organization.city,
        Organization.province,
        Organization.country,
        Organization.postal,
        Organization.longitude,
        Organization.latitude,
        Organization.logo,
        Organization.business_entity_type,
        Organization.industrial_classification_local,
        Organization.parent_organization_number,
        Organization.url,
        Organization.vat_liable,
        Organization.departments_amount
    )
    if description:
        rx = re.compile('([ _\-.,/\\\\])')  # noqa = 605
        description_digit = rx.sub('', description)
        if description_digit.isdigit():
            query = query.filter(Organization.organization_number == description_digit)
        else:
            query = query.filter(or_(
                (Organization.name.ilike(f'%{description}%')),
            ))
    query = query.filter(or_(
        (Organization.departments_amount > 1),
        (Organization.parent_organization_number.is_(None)),
    ))
    query = query.order_by(Organization.parent_organization_number.desc(), Organization.organization_number)

    if description:
        # paging
        page = request.args.get('page', 1, type=int)

        p = query.paginate(page, per_page)
        pages = {'page': page, 'per_page': per_page,
                 'total': p.total, 'pages': p.pages}
        if p.has_prev:
            pages['prev_url'] = url_for(request.endpoint, page=p.prev_num,
                                        per_page=per_page,
                                        expanded=1, _external=True)
        else:
            pages['prev_url'] = None
        if p.has_next:
            pages['next_url'] = url_for(request.endpoint, page=p.next_num,
                                        per_page=per_page,
                                        expanded=1, _external=True)
        else:
            pages['next_url'] = None
        pages['first_url'] = url_for(request.endpoint, page=1,
                                     per_page=per_page, expanded=1,
                                     _external=True)
        pages['last_url'] = url_for(request.endpoint, page=p.pages,
                                    per_page=per_page, expanded=1,
                                    _external=True)
        return {
            'organizations': p.items
            # 'pages': pages
        }
    else:
        page = request.args.get('page', 1, type=int)
        query = query.limit(per_page).offset((page - 1) * per_page)
        return {
            'organizations': query.all(),
        }
