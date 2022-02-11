package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{
	
	public int numGenes = 0; //number of genes
	Random rand = new Random();

	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE
		String chromosomeCopy = String.valueOf(this.getChromosome());
		int length = chromosomeCopy.length();
		//Random rand = new Random();

		String letters = "xyzd";

		boolean changed = false;
		int rand_int1 = 0;
		int rand_int2 = 0;


		char [] chromCopyArr = chromosomeCopy.toCharArray();

		for(int i = 0; i<length; i++)
		{
			if(changed){
				break;
			}
			else {
				rand_int1 = rand.nextInt(100);
				if(70<rand_int1 && rand_int1<81){
					char toChange = chromosomeCopy.charAt(i);
					rand_int2 = rand.nextInt(letters.length());

					char randChar = letters.charAt(rand_int2);
					while(randChar == toChange){
						if(randChar == toChange)
						{
							rand_int2 = rand.nextInt(letters.length());
							randChar = letters.charAt(rand_int2);
						}
					}

					chromCopyArr[i] = randChar;
					changed = true;
				}
			}
		}

		if(!chromCopyArr.toString().equals(chromosomeCopy)){
			copy.setChromosome(chromCopyArr.toString());
		}
		else{
			rand_int1 = rand.nextInt(chromCopyArr.length);
			rand_int2 = rand.nextInt(letters.length());

			char toChange = chromosomeCopy.charAt(rand_int1);
			char randChar = letters.charAt(rand_int2);
			while(randChar == toChange){
				if(randChar == toChange)
				{
					rand_int2 = rand.nextInt(letters.length());
					randChar = letters.charAt(rand_int2);
				}
			}
			chromCopyArr[rand_int1] = randChar;
			copy.setChromosome(chromCopyArr.toString());
		}
		//YOUR CODE GOES ABOVE HERE
		return copy;
	}
	
	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		//YOUR CODE GOES BELOW HERE
		char[] chromosomeCopy1 = String.valueOf(this.getChromosome()).toCharArray();
		char[] chromosomeCopy2 = String.valueOf(mate.getChromosome()).toCharArray();
		int rand_int = 0;
		if(chromosomeCopy1.length<=chromosomeCopy2.length){
			rand_int = rand.nextInt(chromosomeCopy1.length);
		}
		else{
			rand_int = rand.nextInt(chromosomeCopy2.length);
		}


		char[] child1 = new char[rand_int+(chromosomeCopy2.length-rand_int)];
		char[] child2 = new char[rand_int+(chromosomeCopy1.length-rand_int)];
		for(int i = 0; i<child1.length; i++)
		{
			if(i<=rand_int){
				child1[i] = chromosomeCopy1[i];
			}
			else {
				child1[i] = chromosomeCopy2[i];
			}
		}

		for(int i = 0; i<child2.length; i++)
		{
			if(i<=rand_int){
				child2[i] = chromosomeCopy2[i];
			}
			else {
				child2[i] = chromosomeCopy1[i];
			}
		}

		String strChild1 = child1.toString();
		String strChild2 = child2.toString();

		MyDNA offspring1 = new MyDNA();
		offspring1.setChromosome(strChild1);
		MyDNA offspring2 = new MyDNA();
		offspring2.setChromosome(strChild2);

		offspring.add(offspring1);
		offspring.add(offspring2);
		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}
	
	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		//YOUR CODE GOES BELOW HERE
		if(this.getFitness()==other.getFitness())
			result = 0;
		else if(this.getFitness()<other.getFitness())
			result = -1;
		else
			result = 1;
		//YOUR CODE GOES ABOVE HERE
		return result;
	}
	
	
	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE
		
		//YOUR CODE GOES ABOVE HERE
		return s;
	}
	
	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

