from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from oscar.apps.basket import app
from oscar.core.loading import get_class


class BasketApplication(app.BasketApplication):
    basket_add_items_view = get_class('basket.views', 'BasketAddItemsView')
    summary_view = get_class('basket.views', 'BasketSummaryView')

    def get_urls(self):
        urls = [
            url(r'^$', login_required(self.summary_view.as_view()), name='summary'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(), name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$', self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()), name='saved'),
            url(r'^add/$', self.basket_add_items_view.as_view(), name='basket-add'),
        ]
        return self.post_process_urls(urls)


application = BasketApplication()
