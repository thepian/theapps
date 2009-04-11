from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from base import check_http_access
from models import AccessTicket, UsedTicket
from userdata import UserData

def access_permissions(request,template):
    userdata = UserData(affinity=request.affinity,user=request.user)
    if 'ticket' in request.GET:
        try:
            ticket = AccessTicket.objects.grant_access(request.GET['ticket'],request.affinity,request.user,request.affinity_access,None)
            if ticket.entry_path:
                return HttpResponseRedirect(ticket.entry_path)
            
        except AccessTicket.DoesNotExist:
            return HttpResponseForbidden("Ticket not valid")
            
    print request.affinity_access.as_dl()
    q = request.affinity_access.PAGE_QUESTION_TEMPLATE % ("alpha","http","www.idolyzed.local","/")
    print request.affinity_access[q]

    access_tickets = []
    for at in AccessTicket.objects.all():
        if check_http_access(request,level=at.level,domain=at.domain,path=at.path):
            access_tickets.append(at)
            
    used_tickets = []
    #TODO restrict domain search, use_from
    for ut in UsedTicket.objects.filter(device=request.affinity.without_checksum):
        if not request.affinity_access.check_access(level=ut.ticket.level,type=ut.ticket.type,
                domain=ut.ticket.domain,path=ut.ticket.path):
            request.affinity_access.grant_access(level=ut.ticket.level,type=ut.ticket.type,
                domain=ut.ticket.domain,path=ut.ticket.path,use_until=ut.use_until,page=ut.ticket.single_page)
        used_tickets.append(ut.ticket)
        
    return render_to_response(template, {
        "affinity":request.affinity,
        "affinity_access": request.affinity_access,
        "user_access":request.user_access,
        "access_tickets":access_tickets,
        "used_tickets":used_tickets,
        "userdata":userdata
    }, context_instance=RequestContext(request))    
    