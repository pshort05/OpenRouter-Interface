#!/bin/bash
# Network Connectivity Checker for OpenRouter Web Interface

echo "🌐 OpenRouter Network Connectivity Checker"
echo "========================================="

# Get local IP addresses
echo "📍 Network Information:"
echo "  Hostname: $(hostname)"

# Primary local IP (usually the first one)
primary_ip=$(hostname -I | awk '{print $1}')
echo "  Primary IP: $primary_ip"

# Show all IPs
echo "  All IPs:"
ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print "    " $2}' | cut -d'/' -f1

echo ""

# Check if port 5000 is in use
echo "🔍 Checking Port 5000:"
if netstat -tuln 2>/dev/null | grep -q ':5000 '; then
    echo "  ✅ Port 5000 is in use (likely OpenRouter web server)"
    
    # Try to connect locally
    if curl -s -o /dev/null http://localhost:5000 2>/dev/null; then
        echo "  ✅ Local connection successful (http://localhost:5000)"
    else
        echo "  ⚠️  Local connection failed - server may be starting"
    fi
else
    echo "  ❌ Port 5000 is not in use"
    echo "     Run ./start-web.sh to start the server"
fi

echo ""

# Check firewall status (Ubuntu/UFW)
echo "🔥 Firewall Status:"
if command -v ufw >/dev/null 2>&1; then
    ufw_status=$(sudo ufw status 2>/dev/null | grep "Status:" | awk '{print $2}')
    if [ "$ufw_status" = "active" ]; then
        echo "  🔥 UFW Firewall is active"
        
        if sudo ufw status | grep -q "5000"; then
            echo "  ✅ Port 5000 is allowed through firewall"
        else
            echo "  ⚠️  Port 5000 not explicitly allowed"
            echo "     To allow: sudo ufw allow 5000"
        fi
    else
        echo "  ✅ UFW Firewall is inactive"
    fi
else
    echo "  ℹ️  UFW not installed (firewall status unknown)"
fi

echo ""

# Generate access URLs
echo "🌍 Access URLs:"
echo "  📱 Local access:"
echo "    http://localhost:5000"
echo "    http://127.0.0.1:5000"
echo ""
echo "  🌐 Network access (from other devices):"

# Show URLs for each IP
ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1 | while read ip; do
    echo "    http://$ip:5000"
done

echo ""

# Test network connectivity from other devices
echo "📱 Testing from Other Devices:"
echo "  1. Make sure both devices are on the same WiFi/network"
echo "  2. On your phone/tablet/computer, open a web browser"
echo "  3. Navigate to: http://$primary_ip:5000"
echo "  4. You should see the OpenRouter Interface homepage"
echo ""

# Show process information
echo "🔍 Process Information:"
if pgrep -f "flask\|openrouter-web\|run-flask-background" >/dev/null; then
    echo "  ✅ OpenRouter web processes running:"
    pgrep -f "flask\|openrouter-web\|run-flask-background" | while read pid; do
        echo "    PID $pid: $(ps -p $pid -o cmd --no-headers)"
    done
    
    echo ""
    echo "  📝 Log file: openrouter_web.log"
    if [ -f "openrouter_web.log" ]; then
        echo "    Last few lines:"
        tail -3 openrouter_web.log | sed 's/^/      /'
    fi
else
    echo "  ❌ No OpenRouter web processes found"
    echo "     Run ./start-web.sh to start the server"
fi

echo ""
echo "🎯 Quick Actions:"
echo "  • Start server:    ./start-web.sh"
echo "  • View logs:       tail -f openrouter_web.log" 
echo "  • Stop server:     pkill -f 'flask|openrouter-web'"
echo "  • Allow firewall:  sudo ufw allow 5000"