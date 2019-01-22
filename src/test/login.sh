sshpass -p 'Z9K?3{e6Z9K' ssh littledd18@203.145.219.128 -f -L 5001:127.0.0.1:5001 -p 56336 -o StrictHostKeyChecking=no 'cd ai-benchmark/;python v3_web.py' &
#sshpass -p 'Z9K?3{e6Z9K' ssh littledd18@203.145.219.128 -v -L 5001:127.0.0.1:5001 -p 56336 -o StrictHostKeyChecking=no
echo "Hi!!"
