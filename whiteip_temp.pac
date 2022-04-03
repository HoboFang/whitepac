var proxy = 'SOCKS5 127.0.0.1:7890';

// these ips belong to 'CN',but need to be proxied
var exceptionips = {"103.56.16.112": "google.com.hk"};

var specialips = {/*ReplaceSpec*/};

var whiteips = {/*ReplaceWhite*/};

function isIpInList(hostip, iplist) {
    var mask = iplist.mask;
    // can't use bit operation,may get a negative value
    var netip = parseInt(hostip/Math.pow(2, 32-mask)) * Math.pow(2, 32-mask);
    var netip_key = netip.toString();

    if (netip_key in iplist) {
        netip_val = iplist[netip_key];
        if ((typeof netip_val) === 'number') {
            return (hostip < netip + netip_val) ? true : false;
        } else {
            return isIpInList(hostip, netip_val);
        }
    } else {
        return false;
    }
}

function FindProxyForURL(url, host) {
    alert('host = ' + host);
    var host_ip = dnsResolve(host);
    alert('host_ip = ' + host_ip);

    if (host_ip in exceptionips) {
        alert('+++++PROXY+++++');
        return proxy; 
    }

    var ip_arr = host_ip.split('.');
    // can't use convert_addr(),may get a negative value
    var ip_int = 0;
    for (var i=0, b=24; i < 4; i++, b-=8) {
        ip_int += parseInt(ip_arr[i]) * Math.pow(2, b);
    }

    if (isIpInList(ip_int, whiteips) || isIpInList(ip_int, specialips)) {
        alert('-----DERECT-----');
        return "DIRECT";
    } else {
        alert('+++++PROXY+++++');
        return proxy;
    }
}
