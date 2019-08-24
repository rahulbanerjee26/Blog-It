
  

**Blog it!!**

  

<h2>Flask Web App</h2>

  

  

**Used sqlalchemy and flask to complete the project**

**Framework: [Flask](https://palletsprojects.com/p/flask/)** 

**Theme: <a href="https://startbootstrap.com/previews/clean-blog/"> Bootstrap Clean  </a>**

<h3>  <u> Description </u></h3>


  

<p>A app where the user can manage articles. Functionality:

- return Posts and its info in JSON format
- Create Post
- Edit Post
- Delete Post
- View Posts
- Flash messages to improve user experience
</p>

  

  

<h3>  <u> Software Required </u>  </h3>

  
  

<a  href="https://www.virtualbox.org/wiki/Download_Old_Builds_5_1">Virtual Box</a>

  

<a  href="https://www.vagrantup.com/">Vagrant </a>

<a  href="https://www.python.org/downloads/"> Python </a>

<a  href="https://git-scm.com/"> Git Bash </a>

<a  href="https://www.sqlalchemy.org/"> Sqlalchemy </a>

  
  
  

  

<h3>  <u> Steps to Run </u>  </h3>

  

<ul>

  

<li> Install Vagrant and Virtual Box </li>

  

<li> Log in using vagrant ssh </li>

  

<li> Clone Repo </li>

  

<li> Using git bash cd to the folder </li>

  

<li> Create the database by typing

    python setupDB.py
    
    python index.py

</ul>



<h3>  <u> Routes</u>  </h3>
 <b> <i> /  <i> </b> - view posts  
 <br>
 <b> <i> /posts/JSON<i> </b>  - get info about all posts in JSON format
 <br>
  <b> <i>/posts/post_id/JSON<i> </b>  - get info about a specific post in JSON format  
  <br> 
   <b> <i> /post/post_id<i> </b>  - view specific post
   <br>
      <b> <i> /create<i> </b>  - create a post
   <br>
      <b> <i> /post_id/edit<i> </b>  - edit a post
   <br>
    <b> <i> /post_id/delete<i> </b>  - delete a post
   <br>

<h3><u> Author</u>  </h3>

<b>Rahul Banerjee</b>