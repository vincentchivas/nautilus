import urlparse
#from django import forms
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
#from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import get_current_site
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def _login_log(user_name, action, message):
    if not user_name:
        return None
    users = User.objects.filter(username=user_name)
    user_id = users[0].id if users.count() else -1
    LogEntry.objects.log_action(
        user_id=user_id,
        content_type_id=ContentType.objects.get_for_model(User).pk,
        object_id=user_id,
        object_repr=_('login verification'),
        action_flag=action,
        change_message=unicode(message)
    )


@csrf_protect
@never_cache
def custom_login(
        request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
        authentication_form=AuthenticationForm, current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST, request=request)
        user_name = request.POST.get('username')
        if form.is_valid():
            _login_log(user_name, 5, _('login successfully!'))
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            # Security check -- don't allow redirection to a different host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
        else:
            user_cache = form.user_cache
            if user_cache and not user_cache.is_active:
                _login_log(user_name, 5, _('login fail! user isn\'t active!'))
            else:
                _login_log(user_name, 5,
                           _('login fail! invalid user or password!'))

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))


class CustomAdminSite(AdminSite):

    @never_cache
    def login(self, request, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        context = {
            'title': _('Log in'),
            #'root_path': self.root_path,
            'app_path': request.get_full_path(),
            REDIRECT_FIELD_NAME: request.get_full_path(),
        }
        context.update(extra_context or {})
        defaults = {
            'extra_context': context,
            'current_app': self.name,
            'template_name': self.login_template or 'admin/login.html',
        }
        return custom_login(request, **defaults)

custom_site = CustomAdminSite()
