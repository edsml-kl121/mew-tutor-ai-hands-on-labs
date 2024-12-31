echo "Creating villages, houses, and letter..."

mkdir village
cd village
mkdir house1
mkdir house2
mkdir house3

cd house1
touch letter.txt
echo "This is the letter to the first house" > letter.txt
cd ../house2
touch letter.txt
echo "This is the letter to the second house" > letter.txt
cd ../house3
touch letter.txt
echo "This is the letter to the third house" > letter.txt

echo "Done"